from django.conf import settings
from django.contrib.auth.models import User
from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.security.services import LoginToPortalError

from .models import MemberSuitePortalUser
from .services import MemberSuitePortalUserService


def get_user_for_portal_user(portal_user):
    user = None
    user_created = False

    # First, try to match on username.
    user_username = portal_user.generate_username()
    try:
        user = User.objects.get(username=user_username)
    except User.DoesNotExist:
        pass

    # Next, try to match on email address.
    if not user:
        try:
            user = User.objects.filter(email=portal_user.email_address)[0]
        except IndexError:
            pass

    # No match? Create one.
    if not user:
        user = User.objects.create(
            username=user_username,
            email=portal_user.email_address,
            first_name=portal_user.first_name,
            last_name=portal_user.last_name)
        user_created = True

    return user, user_created


class MemberSuiteBackend(object):

    def __init__(self, client=None, user_service=None, *args, **kwargs):
        self.client = client or ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID)
        self.user_service = MemberSuitePortalUserService(client=self.client)

    def authenticate(self, username=None, password=None):
        """Returns the appropriate django.contrib.auth.models.User if
        successful; otherwise returns None.

        If login succeeds and there's no MemberSuitePortalUser that
        matches on membersuite_id;

            1) one is created, and;

            2) a User object might be created too.

        Plus, the is_member attribute on MemberSuitePortalUser is set
        when login succeeds.

        Plus, when a MemberSuitePortalUser is created, the related
        User object gets its names and email updated from MemberSuite.

        Finally, "MAINTENANCE_MODE" is supported, during which all but
        staff logins will fail.

        """
        try:
            authenticated_portal_user = self.user_service.login(
                username=username,
                password=password)
        except LoginToPortalError:
            return None

        try:
            membersuite_portal_user = MemberSuitePortalUser.objects.get(
                membersuite_id=authenticated_portal_user.membersuite_id)

        except MemberSuitePortalUser.DoesNotExist:

            if getattr(settings, "MAINTENANCE_MODE", False):
                return None

            user, user_created = get_user_for_portal_user(
                portal_user=authenticated_portal_user)

            is_member = self.is_member(
                membersuite_portal_user=authenticated_portal_user)

            membersuite_portal_user = MemberSuitePortalUser.objects.create(
                user=user,
                membersuite_id=authenticated_portal_user.membersuite_id,
                is_member=is_member)

            if not user_created:
                # Update User attributes in case they changed
                # in MemberSuite.
                user.email = authenticated_portal_user.email_address
                user.first_name = authenticated_portal_user.first_name
                user.last_name = authenticated_portal_user.last_name

            user.set_unusable_password()  # Do we really want to do this?

            user.save()

        else:
            # Found a MemberSuitePortalUser. Update cached info.
            membersuite_portal_user.is_member = self.is_member(
                membersuite_portal_user=authenticated_portal_user)
            membersuite_portal_user.save()

        if (getattr(settings, "MAINTENANCE_MODE", None) and
            not membersuite_portal_user.user.is_staff):  # noqa

            return None

        return membersuite_portal_user.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def is_member(self, membersuite_portal_user, client=None):
        client = client or self.client

        individual = membersuite_portal_user.get_individual(client=client)
        is_member = individual.is_member(client=client)

        return is_member

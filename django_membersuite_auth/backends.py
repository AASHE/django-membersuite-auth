from django.conf import settings
from django.contrib.auth.models import User
from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.security.services import (
    LoginToPortalError,
    get_user_for_membersuite_entity,
)

from .models import MemberSuitePortalUser
from .services import MemberSuitePortalUserService

from django.db import connection


class MemberSuiteBackend(object):
    def authenticate(self, username=None, password=None):
        """Returns the appropriate django.contrib.auth.models.User if
        successful; otherwise returns None.

        If login succeeds and there's no MemberSuitePortalUser that
        matches on membersuite_id or user;

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
            self.connect()
            user_service = self.get_user_service()
            authenticated_portal_user = user_service.login(
                username=username, password=password
            )
        except LoginToPortalError:
            return None

        # Match on MembersuitePortalUser ID?
        try:
            membersuite_portal_user = MemberSuitePortalUser.objects.get(
                membersuite_id=authenticated_portal_user.membersuite_id
            )

        except MemberSuitePortalUser.DoesNotExist:

            if getattr(settings, "MAINTENANCE_MODE", False):
                return None

            user, user_created = get_user_for_membersuite_entity(
                membersuite_entity=authenticated_portal_user
            )

            # Match on user?
            try:
                membersuite_portal_user = MemberSuitePortalUser.objects.get(user=user)

            except MemberSuitePortalUser.DoesNotExist:

                membersuite_portal_user = MemberSuitePortalUser(
                    user=user, membersuite_id=authenticated_portal_user.membersuite_id
                )

                if not user_created:
                    # Update User attributes in case they changed
                    # in MemberSuite.
                    user.email = authenticated_portal_user.email_address
                    user.first_name = authenticated_portal_user.first_name
                    user.last_name = authenticated_portal_user.last_name

                user.set_unusable_password()

                user.save()

            else:
                membersuite_portal_user.membersuite_id = (
                    authenticated_portal_user.membersuite_id
                )

        # Update cached is_member.
        membersuite_portal_user.is_member = self.get_is_member(
            membersuite_portal_user=authenticated_portal_user
        )

        membersuite_portal_user.org_receives_member_benefits = (
            self.org_receives_member_benefits
        )

        membersuite_portal_user.save()

        if (
            getattr(settings, "MAINTENANCE_MODE", None)
            and not membersuite_portal_user.user.is_staff
        ):  # noqa

            return None

        return membersuite_portal_user.user

    def connect(self):
        self.client = ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID,
        )

    def get_user_service(self):
        user_service = MemberSuitePortalUserService(client=self.client)
        return user_service

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_receives_member_benefits(self, org_membersuite_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT receives_membership_benefits FROM iss_organization join iss_membership on owner_id = account_num  where membersuite_id = %s",
                    [org_membersuite_id],
                )
                receives_member_benefits = cursor.fetchone()

            receives_member_benefits = (
                receives_member_benefits[0]
                if receives_member_benefits[0] != None
                else False
            )

            return receives_member_benefits
        except:
            return False

    def get_is_member(self, membersuite_portal_user, client=None):

        client = client if client else self.client

        individual = membersuite_portal_user.get_individual(client=client)
        organization = individual.get_primary_organization(client=client)
        self.org_receives_member_benefits = self.get_receives_member_benefits(
            organization.membersuite_id
        )

        is_member = individual.is_member(client=client)

        return is_member

from django.conf import settings
from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.security import services
from membersuite_api_client.memberships.services import MembershipService

class MemberSuitePortalUserService(object):
    def __init__(self, client=None):
        self.client = client or ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID,
        )

    def login(self, username, password):
        """Logs `username` into the MemberSuite Portal.

        Returns a .models.MemberSuitePortalUser object if successful,
        raises services.LoginToPortalError if not.

        """
        try:
            return services.login_to_portal(
                username=username, password=password, client=self.client
            )
        except services.LoginToPortalError:
            raise

class MemberSuiteMembershipService(object):
    def __init__(self, client=None):
        self.client = client or ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID,
        )
        self.mem_service = MembershipService(self.client)

    def get_receives_member_benefits(self, account_num):
        """Fetch the current membership for the given account number and return whether receives member benefits."""

        # get the last membership for this account
        all_memberships = self.mem_service.get_memberships_for_org(account_num=account_num)
        last_membership = all_memberships[-1] if all_memberships else None

        receives_member_benefits = (
            last_membership.receives_member_benefits if last_membership else False
        )

        if receives_member_benefits != None:
            print("ORG receives member benefits? %s" % receives_member_benefits)
        else:
            print(
                "ORG receives member benefits? NO MEMBERSHIP INFO HERE for %s"
                % account_num
            )

        return receives_member_benefits

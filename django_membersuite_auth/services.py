from django.conf import settings
from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.security import services


class MemberSuitePortalUserService(object):

    def __init__(self, client=None):
        self.client = client or ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID)

    def login(self, username, password):
        """Logs `username` into the MemberSuite Portal.

        Returns a .models.MemberSuitePortalUser object if successful,
        raises services.LoginToPortalError if not.

        """
        try:
            return services.login_to_portal(username=username,
                                            password=password,
                                            client=self.client)
        except services.LoginToPortalError:
            raise

import os
import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.http import HttpRequest
from django.test import (Client,
                         RequestFactory,
                         TestCase,
                         override_settings)
from django.urls import reverse
from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.security.services import LoginToPortalError

from .backends import MemberSuiteBackend
from .models import MemberSuitePortalUser
from .services import MemberSuitePortalUserService
from .views import LoginView, logout

TEST_MS_PORTAL_USER_ID = os.environ["TEST_MS_PORTAL_USER_ID"]
TEST_MS_PORTAL_USER_PASS = os.environ["TEST_MS_PORTAL_USER_PASS"]


class MemberSuitePortalUserServiceTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(MemberSuitePortalUserServiceTestCase, cls).setUpClass()
        client = ConciergeClient(
            access_key=settings.MS_ACCESS_KEY,
            secret_key=settings.MS_SECRET_KEY,
            association_id=settings.MS_ASSOCIATION_ID)
        cls.user_service = MemberSuitePortalUserService(client=client)

    def test_login(self):
        """Can we login?"""
        membersuite_portal_user = self.user_service.login(
            username=TEST_MS_PORTAL_USER_ID,
            password=TEST_MS_PORTAL_USER_PASS)
        self.assertTrue(membersuite_portal_user.session_id)

    def test_login_failure(self):
        """What happens when we can't login?"""
        with self.assertRaises(LoginToPortalError):
            self.user_service.login(username="bo-o-o-gus user ID",
                                    password="wrong password")


class MemberSuiteBackendTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(MemberSuiteBackendTestCase, cls).setUpClass()
        cls.user_service = MemberSuitePortalUserService()

    def setUp(self):
        self.backend = MemberSuiteBackend(user_service=self.user_service)

    def test_authenticate_username_password_correct(self):
        user = self.backend.authenticate(username=TEST_MS_PORTAL_USER_ID,
                                         password=TEST_MS_PORTAL_USER_PASS)
        self.assertEqual("Test", user.first_name)
        self.assertEqual("User", user.last_name)

    def test_authenticate_bad_username(self):
        self.assertIsNone(
            self.backend.authenticate(
                username="bo-o-o-gus user ID",
                password=TEST_MS_PORTAL_USER_PASS))

    def test_authenticate_bad_password(self):
        self.assertIsNone(
            self.backend.authenticate(
                username=TEST_MS_PORTAL_USER_ID,
                password="wrong password"))

    def test_authenticate_creates_user(self):
        """Is a User created when it should be?

        """
        self.assertEqual(0, User.objects.count())
        user = self.backend.authenticate(
            username=TEST_MS_PORTAL_USER_ID,
            password=TEST_MS_PORTAL_USER_PASS)
        self.assertEqual("Test", user.first_name)
        self.assertEqual("User", user.last_name)

    def test_authenticate_creates_membersuite_portal_user(self):
        """Is a MemberSuitePortalUser created when it should be?

        "When it should be" is when there's not one that matches on
        the MemberSuite ID returned in the result of
        MemberSuitePortalUserService.login().

        """
        self.assertEqual(0, MemberSuitePortalUser.objects.count())
        user = self.backend.authenticate(
            username=TEST_MS_PORTAL_USER_ID,
            password=TEST_MS_PORTAL_USER_PASS)
        membersuite_portal_user = MemberSuitePortalUser.objects.get(user=user)
        self.assertNotEqual("", membersuite_portal_user.membersuite_id)
        self.assertNotEqual("",
                            membersuite_portal_user.membersuite_session_key)

    def test_authenticate_sets_membersuite_session_key(self):
        """Does authenticate() set MemberSuitePortalUser.membersuite_session_key?

        """
        # Authenticate once to get a user/membersuite_portal_user pair.
        user = self.backend.authenticate(username=TEST_MS_PORTAL_USER_ID,
                                         password=TEST_MS_PORTAL_USER_PASS)
        user.membersuiteportaluser.membersuite_session_key = ""
        user.membersuiteportaluser.save()
        # Now authenticate again to reset membersuite_session_key.
        user = self.backend.authenticate(username=TEST_MS_PORTAL_USER_ID,
                                         password=TEST_MS_PORTAL_USER_PASS)
        self.assertNotEqual("",
                            user.membersuiteportaluser.membersuite_session_key)

    @override_settings(MAINTENANCE_MODE=True)
    def test_authenticate_blocks_nonstaff_in_maintenance_mode(self):
        """Does authenticate block non-staff when in Maintenance Mode?
        """
        self.assertIsNone(
            self.backend.authenticate(
                username=TEST_MS_PORTAL_USER_ID,
                password=TEST_MS_PORTAL_USER_PASS))

    def test_is_member_for_member(self):
        """Does is_member() correctly identify a member?

        Assumptions:
          * test user is a member of a member Organization
          * self.user_service.login() succeeds
        """
        membersuite_portal_user = self.user_service.login(
            username=TEST_MS_PORTAL_USER_ID,
            password=TEST_MS_PORTAL_USER_PASS)
        is_member = self.backend.is_member(
            membersuite_portal_user=membersuite_portal_user)
        self.assertTrue(is_member)

    @unittest.skip("Requires fixture of Individual and non-member Org")
    def test_is_member_for_nonmember(self):
        """Does is_member() correctly identify a non-member?
        """
        raise NotImplementedError

    def test_get_user_for_user(self):
        """Does get_user() work for a user?

        """
        user = User.objects.create(username="testusername")
        self.assertEqual(user.username,
                         self.backend.get_user(user_id=user.id).username)

    def test_get_user_for_missing_user(self):
        """How does get_user() work when looking for a missing user?

        """
        self.assertIsNone(self.backend.get_user(user_id=-1))


class ViewsTestCase(TestCase):
    """Tests of functions in views.py

    """
    client = Client()

    def setUp(self):
        self.request_factory = RequestFactory()

    def test_login_get(self):
        response = self.client.get(reverse("django_membersuite_auth_login"))
        self.assertEqual(200, response.status_code)

    def test_logout_then_login(self):
        response = self.client.get(reverse("django_membersuite_auth_logout"))
        self.assertEqual(302, response.status_code)

    def test_login_view_get(self):
        request = self.get_middleworn_request()
        request.method = "GET"
        response = LoginView.as_view()(request)
        self.assertEqual(200, response.status_code)

    def test_logout_with_membersuiteportaluser(self):
        """Does logout work when a MemberSuitePortalUser is attached to
        request.user?

        """
        request = self.get_middleworn_request()
        request.method = "GET"
        request.user = User.objects.create(username="testorato")
        request.user.membersuiteportaluser = (
            MemberSuitePortalUser.objects.create(user=request.user))
        response = logout(request)
        self.assertEqual(200, response.status_code)

    def test_logout_without_membersuiteportaluser(self):
        """Does logout work without a MemberSuitePortalUser attached to
        request.user?

        """
        request = self.get_middleworn_request()
        request.method = "GET"
        request.user = User.objects.create(username="testorato")
        request.user.membersuiteportaluser = None
        response = logout(request)
        self.assertEqual(200, response.status_code)

    def get_middleworn_request(self):
        request = HttpRequest()
        SessionMiddleware().process_request(request)
        return request

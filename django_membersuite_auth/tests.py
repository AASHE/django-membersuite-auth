import os
import unittest

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from membersuite_api_client.client import ConciergeClient
from membersuite_api_client.security.services import LoginToPortalError

from .backends import MemberSuiteBackend
from .models import MemberSuitePortalUser
from .services import MemberSuitePortalUserService


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
        self.assertIsNotNone(user)
        membersuite_portal_user = MemberSuitePortalUser.objects.get(user=user)
        self.assertNotEqual("", membersuite_portal_user.membersuite_id)

    def test_authenticate_blocks_nonstaff_in_maintenance_mode(self):
        """Does authenticate block non-staff when in Maintenance Mode?
        """
        setattr(settings, "MAINTENANCE_MODE", True)
        self.assertIsNone(self.backend.authenticate(
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

    def test_get_user_for_portal_user_match_username(self):
        """Does get_user_for_portal_user work if it finds a username match?
        """
        raise NoImplementedError

    def test_get_user_for_portal_user_match_email(self):
        """Does get_user_for_portal_user work if it finds an email match?
        """
        raise NoImplementedError

    def test_get_user_for_portal_user_no_match(self):
        """Does get_user_for_portal_user work if it finds no match?
        """
        raise NoImplementedError

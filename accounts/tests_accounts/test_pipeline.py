from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import MagicMock
from social_core.exceptions import AuthForbidden
from accounts.pipeline import check_allowed_username, get_username, link_member
from members.models import Member
from unittest.mock import patch


User = get_user_model()


class CheckAllowedUsernameTest(TestCase):
    def setUp(self):
        self.backend = MagicMock()
        self.strategy = MagicMock()

    def test_allowed_username(self):
        Member.objects.create(wiki_username='Allowed User')
        result = check_allowed_username(
            strategy=self.strategy,
            details={'username': 'Allowed User'},
            backend=self.backend
        )
        self.assertIsNone(result)

    def test_forbidden_username(self):
        with self.assertRaises(AuthForbidden):
            check_allowed_username(
                strategy=self.strategy,
                details={'username': 'Forbidden User'},
                backend=self.backend
            )

    def test_empty_username(self):
        with self.assertRaises(AuthForbidden):
            check_allowed_username(
                strategy=self.strategy,
                details={'username': ''},
                backend=self.backend
            )


class GetUsernameTest(TestCase):
    def test_returns_existing_user_username(self):
        user = User.objects.create_user(username='Existing User', password='Test password')
        result = get_username(
            strategy=MagicMock(),
            details={},
            user=user
        )
        self.assertEqual(result, {'username': 'Existing User'})

    def test_returns_username_from_details(self):
        result = get_username(
            strategy=MagicMock(),
            details={'username': 'New User'},
            user=None
        )
        self.assertEqual(result, {'username': 'New User'})


class LinkMemberTest(TestCase):
    def test_links_member_to_user(self):
        member = Member.objects.create(wiki_username='Wiki User')
        user = User.objects.create_user(username='Wiki User', password='Test Password')
        link_member(strategy=MagicMock(), details={}, user=user)
        member.refresh_from_db()
        self.assertEqual(member.user, user)

    def test_does_not_link_if_user_is_none(self):
        Member.objects.create(wiki_username='Wiki User')
        link_member(strategy=MagicMock(), details={}, user=None)
        member = Member.objects.get(wiki_username='Wiki User')
        self.assertIsNone(member.user)

    def test_does_not_overwrite_existing_link(self):
        user1 = User.objects.create_user(username='Wiki user', password='Test Password')
        user2 = User.objects.create_user(username='Wiki user 2', password='Test Password')
        member = Member.objects.create(wiki_username='Wiki User', user=user1)
        link_member(strategy=MagicMock(), details={}, user=user2)
        member.refresh_from_db()
        self.assertEqual(member.user, user1)


class LogLoginTest(TestCase):
    @patch("accounts.pipeline.AuditEntry.log")
    def test_does_nothing_if_user_none(self, mock_log):
        from accounts.pipeline import log_login

        log_login(strategy=MagicMock(), details={}, user=None)

        mock_log.assert_not_called()

    @patch("accounts.pipeline.AuditEntry.log")
    def test_logs_with_username(self, mock_log):
        from accounts.pipeline import log_login

        user = User.objects.create_user(username="TestUser", password="pass")

        log_login(
            strategy=MagicMock(),
            details={"username": "WikiUser"},
            user=user
        )

        mock_log.assert_called_once_with(
            action="user_login",
            actor=str(user),
            payload={"wiki_username": "WikiUser"},
        )

    @patch("accounts.pipeline.AuditEntry.log")
    def test_logs_without_username(self, mock_log):
        from accounts.pipeline import log_login

        user = User.objects.create_user(username="TestUser", password="pass")

        log_login(
            strategy=MagicMock(),
            details={},  # no username
            user=user
        )

        mock_log.assert_called_once_with(
            action="user_login",
            actor=str(user),
            payload={"wiki_username": ""},
        )
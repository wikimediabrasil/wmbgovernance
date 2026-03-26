from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from members.models import Member, MembershipPeriod, DefaultPeriod

User = get_user_model()


class MemberModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='Wiki User', password='Test Password')
        self.member = Member.objects.create(wiki_username='Wiki User', user=self.user)

    def test_str(self):
        self.assertEqual(str(self.member), 'Wiki User')

    def test_wiki_username_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Member.objects.create(wiki_username='Wiki User')

    def test_user_optional(self):
        member = Member.objects.create(wiki_username='No Wiki User')
        self.assertIsNone(member.user)

    def test_one_member_per_user(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Member.objects.create(wiki_username='Other Wiki', user=self.user)


class MembershipPeriodModelTest(TestCase):

    def setUp(self):
        self.member = Member.objects.create(wiki_username='Wiki User')
        self.today = date.today()

    def test_str_with_end_date(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="associate",
            start_date=self.today,
            end_date=self.today + timedelta(days=365)
        )
        self.assertEqual(str(period), _("%(member)s — %(type)s (%(start)s to %(end)s)") % {"member": self.member, "type": "associate", "start": self.today, "end": self.today + timedelta(days=365)})

    def test_str_without_end_date(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="associate",
            start_date=self.today,
        )
        self.assertEqual(str(period), _("%(member)s — %(type)s (since %(start)s)") % {"member": self.member, "type": "associate", "start": self.today})

    def test_is_active_today(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="associate",
            start_date=self.today - timedelta(days=10),
            end_date=self.today + timedelta(days=10)
        )
        self.assertTrue(period.is_active())

    def test_is_not_active_past(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="associate",
            start_date=self.today - timedelta(days=20),
            end_date=self.today - timedelta(days=10)
        )
        self.assertFalse(period.is_active())

    def test_is_not_active_future(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="associate",
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=20)
        )
        self.assertFalse(period.is_active())

    def test_is_active_on_specific_date(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="senior",
            start_date=self.today - timedelta(days=10),
            end_date=self.today + timedelta(days=10)
        )
        self.assertTrue(period.is_active(on_date=self.today))

    def test_associate_type(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="associate",
            start_date=self.today,
            end_date=self.today + timedelta(days=365)
        )
        self.assertEqual(period.membership_type, "associate")

    def test_senior_type(self):
        period = MembershipPeriod.objects.create(
            member=self.member,
            membership_type="senior",
            start_date=self.today,
            end_date=self.today + timedelta(days=365)
        )
        self.assertEqual(period.membership_type, "senior")


class DefaultPeriodModelTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(wiki_username='Wiki User')
        self.today = date.today()

    def test_str(self):
        period = DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today - timedelta(days=10),
            end_date=self.today + timedelta(days=10)
        )
        self.assertIn('Wiki User', str(period))

    def test_is_active_today(self):
        period = DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today - timedelta(days=10),
            end_date=self.today + timedelta(days=10)
        )
        self.assertTrue(period.is_active())

    def test_is_not_active_past(self):
        period = DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today - timedelta(days=20),
            end_date=self.today - timedelta(days=10)
        )
        self.assertFalse(period.is_active())

    def test_is_not_active_future(self):
        period = DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=20)
        )
        self.assertFalse(period.is_active())

    def test_history_preserved(self):
        DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today - timedelta(days=30),
            end_date=self.today - timedelta(days=20)
        )
        DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today - timedelta(days=10),
            end_date=self.today + timedelta(days=10)
        )
        self.assertEqual(self.member.default_periods.count(), 2)

    def test_reason_optional(self):
        period = DefaultPeriod.objects.create(
            member=self.member,
            start_date=self.today,
            end_date=self.today + timedelta(days=10)
        )
        self.assertEqual(period.reason, '')

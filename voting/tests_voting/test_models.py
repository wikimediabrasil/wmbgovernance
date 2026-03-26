from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta, datetime
from members.models import Member, DefaultPeriod
from assemblies.models import Assembly, Agenda, Question, DecisionOptionSet, DecisionOption
from voting.models import Proxy, Vote


def make_assembly():
    return Assembly.objects.create(title='Test Assembly', scheduled_at=timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0)))

def make_agenda(assembly):
    return Agenda.objects.create(assembly=assembly, title='Test Agenda', order=1)

def make_option_set():
    option_set = DecisionOptionSet.objects.create(name='Default')
    DecisionOption.objects.create(option_set=option_set, label='Approve', order=1)
    DecisionOption.objects.create(option_set=option_set, label='Disapprove', order=2)
    return option_set

def make_question(agenda, option_set, status="open"):
    return Question.objects.create(agenda=agenda, text='Should we approve the budget?', order=1, status=status, option_set=option_set)

def make_member(username):
    return Member.objects.create(wiki_username=username)


class ProxyModelTest(TestCase):
    def setUp(self):
        self.assembly = make_assembly()
        self.grantor = make_member('Grantor')
        self.grantee = make_member('Grantee')

    def test_str(self):
        proxy = Proxy.objects.create(assembly=self.assembly, grantor=self.grantor, grantee=self.grantee)
        self.assertIn('Grantor', str(proxy))
        self.assertIn('Grantee', str(proxy))

    def test_grantor_can_only_give_one_proxy_per_assembly(self):
        from django.db import IntegrityError
        third = make_member('Third')
        Proxy.objects.create(assembly=self.assembly, grantor=self.grantor, grantee=self.grantee)
        with self.assertRaises(IntegrityError):
            Proxy.objects.create(assembly=self.assembly, grantor=self.grantor, grantee=third)

    def test_grantee_can_only_receive_one_proxy_per_assembly(self):
        from django.db import IntegrityError
        third = make_member('Third')
        Proxy.objects.create(assembly=self.assembly, grantor=self.grantor, grantee=self.grantee)
        with self.assertRaises(IntegrityError):
            Proxy.objects.create(assembly=self.assembly, grantor=third, grantee=self.grantee)

    def test_grantee_cannot_be_grantor_in_same_assembly(self):
        third = make_member('Third')
        Proxy.objects.create(assembly=self.assembly, grantor=self.grantor, grantee=self.grantee)
        with self.assertRaises(ValidationError):
            proxy = Proxy(assembly=self.assembly, grantor=self.grantee, grantee=third)
            proxy.full_clean()

    def test_grantor_cannot_be_grantee_in_same_assembly(self):
        third = make_member('Third')
        Proxy.objects.create(assembly=self.assembly, grantor=self.grantor, grantee=self.grantee)
        with self.assertRaises(ValidationError):
            proxy = Proxy(assembly=self.assembly, grantor=third, grantee=self.grantor)
            proxy.full_clean()


class VoteModelTest(TestCase):
    def setUp(self):
        self.assembly = make_assembly()
        self.agenda = make_agenda(self.assembly)
        self.option_set = make_option_set()
        self.question = make_question(self.agenda, self.option_set)
        self.option = self.option_set.options.get(label='Approve')
        self.member = make_member('Voter')

    def test_str(self):
        vote = Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        self.assertIn('Voter', str(vote))

    def test_direct_vote(self):
        vote = Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        self.assertIsNone(vote.proxy)
        self.assertEqual(vote.on_behalf_of, self.member)

    def test_cannot_vote_on_pending_question(self):
        question = make_question(self.agenda, self.option_set, status="pending")
        vote = Vote(question=question, voter=self.member, on_behalf_of=self.member, option=self.option)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_cannot_vote_on_closed_question(self):
        question = make_question(self.agenda, self.option_set, status="closed")
        vote = Vote(question=question, voter=self.member, on_behalf_of=self.member, option=self.option)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_cannot_vote_with_wrong_option(self):
        other_set = DecisionOptionSet.objects.create(name='Other')
        wrong_option = DecisionOption.objects.create(option_set=other_set, label='Other', order=1)
        vote = Vote(question=self.question, voter=self.member, on_behalf_of=self.member, option=wrong_option)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_defaulting_member_cannot_vote(self):
        DefaultPeriod.objects.create(member=self.member, start_date=date.today() - timedelta(days=10), end_date=date.today() + timedelta(days=10))
        vote = Vote(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_each_member_voted_for_once_per_question(self):
        from django.db import IntegrityError
        Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        with self.assertRaises(IntegrityError):
            Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)

    def test_proxy_vote(self):
        grantor = make_member('Grantor')
        proxy = Proxy.objects.create(assembly=self.assembly, grantor=grantor, grantee=self.member)
        vote = Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=grantor, option=self.option, proxy=proxy)
        self.assertEqual(vote.proxy, proxy)
        self.assertEqual(vote.on_behalf_of, grantor)

    def test_grantee_cannot_vote_proxy_if_grantor_already_voted(self):
        grantor = make_member('Grantor')
        proxy = Proxy.objects.create(assembly=self.assembly, grantor=grantor, grantee=self.member)
        Vote.objects.create(question=self.question, voter=grantor, on_behalf_of=grantor, option=self.option)
        vote = Vote(question=self.question, voter=self.member, on_behalf_of=grantor, option=self.option, proxy=proxy)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_grantor_cannot_vote_if_grantee_already_voted_on_behalf(self):
        grantor = make_member('Grantor')
        proxy = Proxy.objects.create(assembly=self.assembly, grantor=grantor, grantee=self.member)
        Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=grantor, option=self.option, proxy=proxy)
        vote = Vote(question=self.question, voter=grantor, on_behalf_of=grantor, option=self.option)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_invalid_proxy_for_assembly(self):
        other_assembly = make_assembly()
        grantor = make_member('Grantor')
        proxy = Proxy.objects.create(assembly=other_assembly, grantor=grantor, grantee=self.member)
        vote = Vote(question=self.question, voter=self.member, on_behalf_of=grantor, option=self.option, proxy=proxy)
        with self.assertRaises(ValidationError):
            vote.full_clean()

    def test_wrong_grantee_cannot_use_proxy(self):
        grantor = make_member('Grantor')
        other_member = make_member('Other')
        proxy = Proxy.objects.create(assembly=self.assembly, grantor=grantor, grantee=self.member)
        vote = Vote(question=self.question, voter=other_member, on_behalf_of=grantor, option=self.option, proxy=proxy)
        with self.assertRaises(ValidationError):
            vote.full_clean()

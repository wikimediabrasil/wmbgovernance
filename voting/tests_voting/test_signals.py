from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from members.models import Member
from assemblies.models import Assembly, Agenda, Question, DecisionOptionSet, DecisionOption, Attendance
from voting.models import Proxy, Vote


def make_assembly():
    return Assembly.objects.create(title='Test Assembly', scheduled_at=timezone.make_aware(datetime(2024, 1, 1, 10, 0, 0)))

def make_agenda(assembly):
    return Agenda.objects.create(assembly=assembly, title='Test Agenda', order=1)

def make_option_set():
    option_set = DecisionOptionSet.objects.create(name='Default')
    DecisionOption.objects.create(option_set=option_set, label='Approve', order=1)
    return option_set

def make_question(agenda, option_set):
    return Question.objects.create(agenda=agenda, text='Should we approve the budget?', order=1, status="open", option_set=option_set)

def make_member(username):
    return Member.objects.create(wiki_username=username)


class AttendanceSignalTest(TestCase):

    def setUp(self):
        self.assembly = make_assembly()
        self.agenda = make_agenda(self.assembly)
        self.option_set = make_option_set()
        self.question = make_question(self.agenda, self.option_set)
        self.option = self.option_set.options.first()
        self.member = make_member('voter')

    def test_direct_vote_registers_attendance(self):
        Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        self.assertTrue(Attendance.objects.filter(question=self.question, member=self.member, by_proxy=False).exists())

    def test_proxy_vote_registers_grantor_attendance_by_proxy(self):
        grantor = make_member('grantor')
        proxy = Proxy.objects.create(assembly=self.assembly, grantor=grantor, grantee=self.member)
        Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=grantor, option=self.option, proxy=proxy)
        self.assertTrue(Attendance.objects.filter(question=self.question, member=grantor, by_proxy=True).exists())

    def test_voting_twice_does_not_duplicate_attendance(self):
        Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        self.assertEqual(Attendance.objects.filter(question=self.question, member=self.member).count(), 1)

    def test_attendance_not_created_on_vote_update(self):
        vote = Vote.objects.create(question=self.question, voter=self.member, on_behalf_of=self.member, option=self.option)
        Attendance.objects.filter(question=self.question, member=self.member).delete()
        vote.save()
        self.assertFalse(Attendance.objects.filter(question=self.question, member=self.member).exists())

from datetime import datetime
from django.test import TestCase
from datetime import date
from assemblies.models import Assembly, Agenda, Question, DecisionOptionSet, DecisionOption, Attendance
from members.models import Member


class AssemblyModelTest(TestCase):
    def setUp(self):
        self.today = date.today()
        self.assembly = Assembly.objects.create(title='Test Assembly', scheduled_at=datetime(2024, 1, 1, 10, 0, 0))

    def test_str(self):
        self.assertIn('Test Assembly', str(self.assembly))

    def test_ordering(self):
        assembly2 = Assembly.objects.create(title='Test Assembly 2', scheduled_at='2024-02-01 10:00:00')
        assemblies = Assembly.objects.all()
        self.assertEqual(assemblies[0], assembly2)


class AgendaModelTest(TestCase):
    def setUp(self):
        self.assembly = Assembly.objects.create(title='Test Assembly', scheduled_at='2024-01-01 10:00:00')
        self.agenda = Agenda.objects.create( assembly=self.assembly, title='Test Agenda', order=1)

    def test_str(self):
        self.assertEqual(str(self.agenda), 'Test Agenda')

    def test_ordering(self):
        agenda2 = Agenda.objects.create(
            assembly=self.assembly,
            title='Test Agenda 2',
            order=2
        )
        agendas = Agenda.objects.all()
        self.assertEqual(agendas[0], self.agenda)
        self.assertEqual(agendas[1], agenda2)

    def test_belongs_to_assembly(self):
        self.assertEqual(self.agenda.assembly, self.assembly)


class DecisionOptionSetModelTest(TestCase):
    def setUp(self):
        self.option_set = DecisionOptionSet.objects.create(
            name='Default',
            description='Default option set'
        )

    def test_str(self):
        self.assertEqual(str(self.option_set), 'Default')

    def test_name_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DecisionOptionSet.objects.create(name='Default')


class DecisionOptionModelTest(TestCase):
    def setUp(self):
        self.option_set = DecisionOptionSet.objects.create(name='Default')
        self.option = DecisionOption.objects.create(
            option_set=self.option_set,
            label='Approved',
            order=1
        )

    def test_str(self):
        self.assertIn('Approved', str(self.option))

    def test_ordering(self):
        option2 = DecisionOption.objects.create(
            option_set=self.option_set,
            label='Denied',
            order=2
        )
        options = DecisionOption.objects.all()
        self.assertEqual(options[0], self.option)
        self.assertEqual(options[1], option2)

    def test_belongs_to_option_set(self):
        self.assertEqual(self.option.option_set, self.option_set)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.assembly = Assembly.objects.create(
            title='Test Assembly',
            scheduled_at='2024-01-01 10:00:00'
        )
        self.agenda = Agenda.objects.create(
            assembly=self.assembly,
            title='Test Agenda',
            order=1
        )
        self.option_set = DecisionOptionSet.objects.create(name='Default')
        self.question = Question.objects.create(
            agenda=self.agenda,
            text='Should we approve the budget?',
            order=1,
            status="pending",
            option_set=self.option_set
        )

    def test_str(self):
        self.assertIn('Should we approve', str(self.question))

    def test_default_status_is_pending(self):
        self.assertEqual(self.question.status, "pending")

    def test_status_transitions(self):
        self.question.status = "open"
        self.question.save()
        self.question.refresh_from_db()
        self.assertEqual(self.question.status, "open")

        self.question.status = "closed"
        self.question.save()
        self.question.refresh_from_db()
        self.assertEqual(self.question.status, "closed")

    def test_option_set_protected(self):
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.option_set.delete()

    def test_ordering(self):
        question2 = Question.objects.create(
            agenda=self.agenda,
            text='Second question',
            order=2,
            status="pending",
            option_set=self.option_set
        )
        questions = Question.objects.all()
        self.assertEqual(questions[0], self.question)
        self.assertEqual(questions[1], question2)


class AttendanceModelTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(wiki_username='Wiki User')
        self.assembly = Assembly.objects.create(
            title='Test Assembly',
            scheduled_at='2024-01-01 10:00:00'
        )
        self.agenda = Agenda.objects.create(
            assembly=self.assembly,
            title='Test Agenda',
            order=1
        )
        self.option_set = DecisionOptionSet.objects.create(name='Default')
        self.question = Question.objects.create(
            agenda=self.agenda,
            text='Should we approve the budget?',
            order=1,
            status="open",
            option_set=self.option_set
        )

    def test_str(self):
        attendance = Attendance.objects.create(
            question=self.question,
            member=self.member
        )
        self.assertIn('Wiki User', str(attendance))

    def test_unique_together(self):
        from django.db import IntegrityError
        Attendance.objects.create(
            question=self.question,
            member=self.member
        )
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                question=self.question,
                member=self.member
            )

    def test_registered_by_admin_default_false(self):
        attendance = Attendance.objects.create(
            question=self.question,
            member=self.member
        )
        self.assertFalse(attendance.registered_by_admin)

    def test_by_proxy_default_false(self):
        attendance = Attendance.objects.create(
            question=self.question,
            member=self.member
        )
        self.assertFalse(attendance.by_proxy)

    def test_registered_by_admin(self):
        attendance = Attendance.objects.create(
            question=self.question,
            member=self.member,
            registered_by_admin=True
        )
        self.assertTrue(attendance.registered_by_admin)

    def test_by_proxy(self):
        attendance = Attendance.objects.create(
            question=self.question,
            member=self.member,
            by_proxy=True
        )
        self.assertTrue(attendance.by_proxy)

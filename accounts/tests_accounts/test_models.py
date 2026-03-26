from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(username='Test User', password='Test Password')
        self.assertEqual(user.username, 'Test User')

    def test_str(self):
        user = User.objects.create_user(username='Test User', password='Test Password')
        self.assertEqual(str(user), 'Test User')


class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='Test User', password='Test Password')
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_created_via_signal(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_str_with_display_name(self):
        self.profile.display_name = 'Test User'
        self.profile.save()
        self.assertEqual(str(self.profile), 'Test User')

    def test_str_without_display_name(self):
        self.assertEqual(str(self.profile), 'Test User')

    def test_profile_fields(self):
        self.profile.email = 'email@test.com'
        self.profile.phone = '(11)9-0000-0000'
        self.profile.address_line1 = 'Rua dos Bobos, 0, apto. A'
        self.profile.city = 'São Paulo'
        self.profile.state = 'São Paulo'
        self.profile.postal_code = '00000-000'
        self.profile.country = 'Brasil'
        self.profile.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.email, 'email@test.com')
        self.assertEqual(self.profile.phone, '(11)9-0000-0000')
        self.assertEqual(self.profile.city, 'São Paulo')
        self.assertEqual(self.profile.country, 'Brasil')

    def test_profile_default_country(self):
        self.assertEqual(self.profile.country, 'Brasil')

    def test_only_one_profile_per_user(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user)
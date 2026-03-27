from django.test import TestCase
from django.urls import reverse
from accounts.models import User, Profile


class LoginViewTest(TestCase):
    def test_login_redirects_to_mediawiki(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('mediawiki', response['Location'])

    def test_logout_redirects_to_index(self):
        user = User.objects.create_user(username='Test User', password='Test password')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:index'))

    def test_logout_logs_user_out(self):
        user = User.objects.create_user(username='Test User', password='Test password')
        self.client.force_login(user)
        self.client.get(reverse('accounts:logout'))
        response = self.client.get(reverse('accounts:index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_forbidden_view_returns_403(self):
        response = self.client.get(reverse('accounts:forbidden'))
        self.assertEqual(response.status_code, 403)

    def test_forbidden_view_uses_template(self):
        response = self.client.get(reverse('accounts:forbidden'))
        self.assertTemplateUsed(response, 'accounts/forbidden.html')


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test User', password='Test password')
        self.profile = Profile.objects.get(user=self.user)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
                             fetch_redirect_response=False)

    def test_get_profile_page_if_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertIn("form", response.context)

    def test_post_valid_form(self):
        self.client.force_login(self.user)
        data = { "country": "Nárnia" }

        self.assertEqual(self.profile.country,"Brasil")

        response = self.client.post(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.country,"Nárnia")

    def test_post_invalid_form(self):
        self.client.force_login(self.user)
        data = { "phone": "9"*50 }

        response = self.client.post(reverse('accounts:profile'), data)
        form = response.context["form"]

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.profile.phone,"9"*50)
        self.assertIn("phone", form.errors)
        self.assertIn("country", form.errors)

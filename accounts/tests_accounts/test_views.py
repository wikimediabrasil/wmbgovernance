from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


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
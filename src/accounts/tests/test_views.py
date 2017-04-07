from django.test import TestCase
from unittest.mock import patch, call

from accounts.models import Token

class SendLoginEmailViewTest(TestCase):

    @patch('accounts.views.send_mail')
    def test_redirect_to_home_page(self, mock_send_mail):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'a@b.com'
        })
        self.assertRedirects(response, '/')

    @patch('accounts.views.send_mail')
    def test_send_mail_to_address_from_post(self, mock_send_mail):
        self.client.post('/accounts/send_login_email', data={
            'email': 'a@b.com'
        })

        self.assertTrue(mock_send_mail.send_mail_called)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for tdd')
        self.assertEqual(from_email, 'noreply@lttviet.com')
        self.assertEqual(to_list, ['a@b.com'])

    @patch('accounts.views.send_mail')
    def test_add_success_message(self, mock_send_mail):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'a@b.com'
        }, follow=True)

        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message,
            "Check your email, we've sent you a link you can use to login"
        )
        self.assertEqual(message.tags, 'success')

    def test_creates_token_associated_with_email(self):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'a@b.com'
        })
        token = Token.objects.first()
        self.assertEqual(token.email, 'a@b.com')

    @patch('accounts.views.send_mail')
    def test_send_link_to_login_using_uid(self, mock_send_mail):
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'a@b.com'
        })
        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)

@patch('accounts.views.auth')
class LoginViewTest(TestCase):

    def test_redirect_to_home_page(self, mock_auth):
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(
            mock_auth.authenticate.call_args,
            call(uid='abcd123')
        )

    def test_call_auth_login_with_user_if_there_is_one(self, mock_auth):
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(
            mock_auth.login.call_args,
            call(response.wsgi_request, mock_auth.authenticate.return_value)
        )

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth):
        mock_auth.authenticate.return_value = None
        self.client.get('/accounts/login?token=abcd123')
        self.assertFalse(mock_auth.login.called)

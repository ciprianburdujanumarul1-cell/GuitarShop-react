import pyotp
from django.test import TestCase
from django.contrib.auth.models import User
from mainpage.models import TwoFactorDevice

class TwoFactorLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.com', password='Str0ng!Pass')
        self.device = TwoFactorDevice.objects.create(user=self.user, is_enabled=True)

    def test_login_without_code_requires_2fa(self):
        res = self.client.post('/api/auth/login/', {'email': 'test@test.com', 'password': 'Str0ng!Pass'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('requires_2fa', res.data)

    def test_login_with_valid_code_succeeds(self):
        code = pyotp.TOTP(self.device.secret).now()
        res = self.client.post('/api/auth/login/', {
            'email': 'test@test.com', 'password': 'Str0ng!Pass', 'code': code
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)

    def test_login_with_wrong_code_fails(self):
        res = self.client.post('/api/auth/login/', {
            'email': 'test@test.com', 'password': 'Str0ng!Pass', 'code': '000000'
        })
        self.assertEqual(res.status_code, 400)
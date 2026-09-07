from django.db import models
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import pyotp

# Create your models here.




class TwoFactorDevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='twofa')
    secret = models.CharField(max_length=32, default=pyotp.random_base32)
    is_enabled = models.BooleanField(default=False)

    def get_totp(self):
        return pyotp.TOTP(self.secret)
class Userdetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='detail')
    country = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=128)
    def clean(self):
        try:
            validate_password(self.password)
        except ValidationError as e:
            raise ValidationError({'password': e.messages})
    def __str__(self):
        return self.user.username
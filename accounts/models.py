from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField


class User(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = EncryptedCharField(_("Name"), max_length=255, blank=True, help_text=_("Your name"))
    email = EncryptedEmailField(_("Email address"), blank=True, help_text=_("Your email address. e.g.: email@email.com"))
    phone = EncryptedCharField(_("Telephone number"), max_length=30, blank=True, help_text=_("Your telephone number, with DDD or DDI"))
    address = EncryptedCharField(_("Address"), max_length=500, blank=True, help_text=_("Your address for correspondences. e.g.: Avenida Paulista, 2278, andar Pilotis - Bela Vista"))
    city = EncryptedCharField(_("City"), max_length=100, blank=True, help_text=_("The city you are residing. e.g.: São Paulo"))
    state = EncryptedCharField(_("State"), max_length=100, blank=True, help_text=_("The state you are residing. e.g.: São Paulo"))
    postal_code = EncryptedCharField(_("Postal code"), max_length=20, blank=True, help_text=_("The postal code of your address. e.g.:01.310-300"))
    country = EncryptedCharField(_("Country"), max_length=100, default='Brasil', help_text=_("The country you are residing. e.g.: Brazil"))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return self.display_name or self.user.username


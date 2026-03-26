from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField


class Member(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='member' )
    wiki_username = models.CharField(_("Wiki username"), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    def __str__(self):
        return self.wiki_username


class MembershipPeriod(models.Model):
    TYPE_CHOICES = [('associate', _('Associate')), ('senior', _('Senior'))]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='membership_periods')
    membership_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def is_active(self, on_date=None):
        from datetime import date
        on_date = on_date or date.today()
        return self.start_date <= on_date and (self.end_date is None or self.end_date >= on_date)

    def __str__(self):
        if not self.end_date:
            return _("%(member)s — %(type)s (since %(start)s)") % {"member": self.member, "type": self.membership_type, "start": self.start_date}
        return _("%(member)s — %(type)s (%(start)s to %(end)s)") % {"member": self.member, "type": self.membership_type, "start": self.start_date, "end": self.end_date}


class DefaultPeriod(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='default_periods')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = EncryptedCharField(blank=True)

    class Meta:
        verbose_name = _('Default Period')
        verbose_name_plural = _('Default Periods')

    def is_active(self, on_date=None):
        from datetime import date
        on_date = on_date or date.today()
        return self.start_date <= on_date <= self.end_date

    def __str__(self):
        return _("%(member)s — %(start_date)s to %(end_date)s") % {"member": self.member, "start_date": self.start_date, "end_date": self.end_date}
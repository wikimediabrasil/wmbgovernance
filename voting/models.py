from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from django.utils.translation import gettext_lazy as _


class Proxy(models.Model):
    assembly = models.ForeignKey('assemblies.Assembly', on_delete=models.CASCADE, related_name='proxies')
    grantor = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='proxies_granted')
    grantee = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='proxies_received')

    class Meta:
        verbose_name = _("Proxy")
        verbose_name_plural = _("Proxies")
        unique_together = [
            ('assembly', 'grantor'),
            ('assembly', 'grantee'),
        ]

    def clean(self):
        # grantee cannot be a grantor in the same assembly
        if Proxy.objects.filter(assembly=self.assembly, grantor=self.grantee).exists():
            raise ValidationError(_("%(grantee)s is a grantee in this assembly and therefore cannot be a grantor") % {'grantee': self.grantee})

        # grantor cannot be a grantee in the same assembly
        if Proxy.objects.filter(assembly=self.assembly, grantee=self.grantor).exists():
            raise ValidationError(_("%(grantor)s is already a grantor in this assembly and therefore cannot be a grantee.") % {'grantor': self.grantor})


    def __str__(self):
        return _("%(grantee)s represents %(grantor)s in %(assembly)s") % {'grantee': self.grantee, 'grantor': self.grantor, 'assembly': self.assembly}


class Vote(models.Model):
    question = models.ForeignKey('assemblies.Question', on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='votes')
    on_behalf_of = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='votes_received')
    option = models.ForeignKey('assemblies.DecisionOption', on_delete=models.PROTECT, related_name='votes')
    proxy = models.ForeignKey(Proxy, on_delete=models.PROTECT, null=True, blank=True, related_name='votes')
    cast_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'voto'
        verbose_name_plural = 'votos'
        unique_together = [
            ('question', 'on_behalf_of'),
        ]

    def __str__(self):
        return f"{self.on_behalf_of} — {self.question}"

    def clean(self):
        try:
            question = self.question
        except Exception:
            return
        try:
            voter = self.voter
        except Exception:
            return

        if question.status != 'open':
            raise ValidationError(_("This question is not open for voting yet."))
        if self.option.option_set != question.option_set:
            raise ValidationError(_("Invalid option for this question."))
        if voter.default_periods.filter(start_date__lte=date.today(), end_date__gte=date.today()).exists():
            raise ValidationError(_("Member is in default, and therefore can not vote."))
        if self.proxy:
            if self.proxy.assembly != question.agenda.assembly:
                raise ValidationError(_("This proxy is not valid for this assembly."))
            if self.proxy.grantee != voter:
                raise ValidationError(_("You are not the designated grantee"))
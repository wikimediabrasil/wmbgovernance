from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField


class Assembly(models.Model):
    title = models.CharField(_("Title"), max_length=255, help_text=_("Title of the assembly."))
    description = models.TextField(_("Description"), blank=True, help_text=_("Description of the assembly."))
    scheduled_at = models.DateTimeField(_("Scheduled at"))

    class Meta:
        verbose_name = _('Assembly')
        verbose_name_plural = _('Assemblies')
        ordering = ['-scheduled_at']

    def __str__(self):
        scheduled_at = f"{self.scheduled_at:\%Y-\%m-\%d}"
        return _("%(title)s (%(scheduled_at)s)") % {'title': self.title, 'scheduled_at': self.scheduled_at}


class Agenda(models.Model):
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='agendas')
    title = models.CharField(_("Title"), max_length=255, help_text=_("Title of the agenda item."))
    order = models.PositiveIntegerField(_("Order"), default=0, help_text=_("Order of the agenda item."))

    class Meta:
        verbose_name = _('Agenda')
        verbose_name_plural = _('Agendas')
        ordering = ['order']

    def __str__(self):
        return self.title


class DecisionOptionSet(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True, help_text=_("Name of the decision option set"))
    description = models.TextField(_("Description"), blank=True, help_text=_("Description of the decision option set."))

    class Meta:
        verbose_name = _("Decision option set")
        verbose_name_plural = _("Decision option sets")

    def __str__(self):
        return self.name


class DecisionOption(models.Model):
    option_set = models.ForeignKey(DecisionOptionSet, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(_("Label"), max_length=255, help_text=_("label for this option"))  # ex: 'Favorável', 'Contrário', 'Abstenção'
    order = models.PositiveIntegerField(_("Order"), default=0, help_text=_("Order of the option"))

    class Meta:
        verbose_name = _("Decision option")
        verbose_name_plural = _("Decision options")
        ordering = ['order']

    def __str__(self):
        return self.label


class Question(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Waiting")),
        ("open", _("Opened")),
        ("closed", _("Closed")),
    ]

    agenda = models.ForeignKey(Agenda, on_delete=models.CASCADE, related_name='questions')
    text = EncryptedCharField(_("Text"), help_text=_("Question text."))
    order = models.PositiveIntegerField(_("Order"), default=0, help_text=_("Order of the question."))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="pending", help_text=_("Status of the question."))
    option_set = models.ForeignKey(DecisionOptionSet,on_delete=models.PROTECT, related_name='questions')
    opened_at = models.DateTimeField(_("Opened"), null=True, blank=True, help_text=_("When this question was opened."))
    closed_at = models.DateTimeField(_("Closed"), null=True, blank=True, help_text=_("When this question was closed."))

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['order']

    def __str__(self):
        return self.text[:80]


class Attendance(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attendances')
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE, related_name='attendances')
    registered_at = models.DateTimeField(_("Registered at"), auto_now_add=True, help_text=_("When this attendance was registered."))
    registered_by_admin = models.BooleanField(_("Was it registered by an admin?"), default=False, help_text=_("Whether this attendance was registered by an admin."))
    by_proxy = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")
        unique_together = [('question', 'member')]

    def __str__(self):
        return f"{self.member} — {self.question}"
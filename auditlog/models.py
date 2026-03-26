import hashlib
import json
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from encrypted_model_fields.fields import EncryptedCharField, EncryptedTextField


class AuditEntry(models.Model):
    ACTION_CHOICES = [
        ('vote_cast', _('Vote cast')),
        ('vote_edited', _('Vote edited')),
        ('question_opened', _('Question opened')),
        ('question_closed', _('Question closed')),
        ('user_login', _('User login')),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    actor = EncryptedCharField(max_length=255)
    payload = EncryptedCharField(max_length=5000)
    previous_hash = models.CharField(max_length=64)
    entry_hash = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = _('Audit entry')
        verbose_name_plural = _('Audit entries')

    def __str__(self):
        return f"{self.timestamp} — {self.action} — {self.actor}"

    @classmethod
    def get_last_hash(cls):
        last = cls.objects.order_by('-timestamp').first()
        return last.entry_hash if last else '0' * 64

    @classmethod
    def log(cls, action, actor, payload):
        with transaction.atomic():
            last = cls.objects.select_for_update().order_by('-timestamp').first()
            previous_hash = last.entry_hash if last else '0' * 64

            payload_str = json.dumps(payload, sort_keys=True, default=str)

            raw = json.dumps({
                'action': action,
                'actor': actor,
                'payload': payload_str,
                'previous_hash': previous_hash,
            }, sort_keys=True, default=str)
            entry_hash = hashlib.sha256(raw.encode()).hexdigest()

            return cls.objects.create(
                action=action,
                actor=actor,
                payload=payload_str,  # always a JSON string
                previous_hash=previous_hash,
                entry_hash=entry_hash,
            )

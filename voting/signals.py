from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vote
from assemblies.models import Attendance


@receiver(post_save, sender=Vote)
def register_attendance(sender, instance, created, **kwargs):
    if not created:
        return

    Attendance.objects.get_or_create(
        question=instance.question,
        member=instance.on_behalf_of,
        defaults={'registered_by_admin': False, 'by_proxy': instance.proxy is not None}
    )

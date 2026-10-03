
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Document
from apps.notification.models import Notification


@receiver(pre_save, sender=Document)
def old_data(sender, instance, **kwargs):
    """Capture the previous document status before saving."""
    if not instance.pk:
        instance._old_status = None
        return

    try:
        previous_data = Document.objects.get(pk=instance.pk)
        instance._old_status = previous_data.status
    except Document.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Document)
def document_notifications(sender, instance, created, **kwargs):
    """Create notifications and send them through WebSockets."""
    channel_layer = get_channel_layer()
    group_name = f"user-{instance.user_id}"
    message = None

    if created:
        message = (
            f"🎉 📄 '{instance.title}' uploaded successfully!\n"
            "✨ Your document is ready for processing."
        )

        Notification.objects.create(
            user=instance.user,
            title="🎉 Document Uploaded",
            message=message,
            notification_type=Notification.Type.DOCUMENT,
            data={
                "id": instance.id,
            },
        )

    else:
        old_status = getattr(instance, "_old_status", None)

        # Notify only when the document status actually changes.
        if old_status is None or old_status == instance.status:
            return

        status_messages = {
            "PENDING": "⏳ Waiting to be processed...",
            "PROCESSING": "⚙️ Your document is being processed...",
            "READY": "✅ Your document is ready!",
            "FAILED": "❌ Document processing failed. Please try again.",
        }

        status_emoji = {
            "PENDING": "⏳",
            "PROCESSING": "⚙️",
            "READY": "🎉",
            "FAILED": "🚨",
        }

        emoji = status_emoji.get(instance.status, "🔔")
        status_text = status_messages.get(
            instance.status,
            f"📌 Status updated to {instance.status}.",
        )

        message = (
            f"{emoji} 📄 '{instance.title}'\n"
            f"🔄 {old_status} ➜ {instance.status}\n"
            f"{status_text}"
        )

        Notification.objects.create(
            user=instance.user,
            title=f"{emoji} Document Status Updated",
            message=message,
            notification_type=Notification.Type.DOCUMENT,
            data={
                "id": instance.id,
                "old_status": old_status,
                "new_status": instance.status,
            },
        )

    if message and channel_layer:
        event = {
            "type": "notification",
            "message": message,
        }

        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver([post_save, post_delete], sender=Document)
def clear_cache(sender, instance, **kwargs):
    """Clear the user's dashboard cache after document changes."""
    prefix = f"dashboard-{instance.user_id}"
    cache.delete(prefix)

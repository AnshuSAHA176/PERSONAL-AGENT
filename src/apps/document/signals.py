from django.db.models.signals import post_save,post_delete,pre_save
from django.dispatch import receiver
from .models import Document
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



@receiver(pre_save,sender=Document)
def old_data(sender, instance, **kwargs):
     ...


@receiver(post_save,sender=Document)
def documnet_notifications(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f"user-{instance.user_id}"
    message = None
    if created:
            message = "Document upload successfully"



    

    if message:
        event = {
                "type": "notification_message",
                "message": f'{"\n".join(message)}"\n"{instance.status}',

            }

        async_to_sync(
                channel_layer.group_send
            )(
                group_name,
                event
            )
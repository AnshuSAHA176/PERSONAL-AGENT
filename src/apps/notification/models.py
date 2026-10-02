
from django.conf import settings
from django.db import models


class Notification(models.Model):

    class Type(models.TextChoices):
        DOCUMENT = "DOCUMENT", "Document"
        NIGHTLY_BRAIN = "NIGHTLY_BRAIN", "Nightly Brain"
        BRIEFING = "BRIEFING", "Briefing"
        SYSTEM = "SYSTEM", "System"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices
    )

    is_read = models.BooleanField(default=False)

    data = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_read", "-created_at"],
                name="notif_user_read_created_idx"
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.user}"



from django.conf import settings
from django.db import models


class NightlySession(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nightly_sessions",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "-started_at"]),
        ]

    def __str__(self):
        return f"Session {self.id} - {self.user_id} - {self.status}"


class Discovery(models.Model):
    class DiscoveryType(models.TextChoices):
        TOPIC = "TOPIC", "Topic"
        CONNECTION = "CONNECTION", "Connection"
        INSIGHT = "INSIGHT", "Insight"

    session = models.ForeignKey(
        NightlySession, on_delete=models.CASCADE, related_name="discoveries"
    )
    discovery_type = models.CharField(max_length=20, choices=DiscoveryType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()

    # IDs and references to the documents and chunks
    # that support this discovery.
    source_references = models.JSONField(default=list, blank=True)

    # Flexible metadata for future discovery features.
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session", "discovery_type"]),
        ]

    def __str__(self):
        return self.title


class Recommendation(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        COMPLETED = "COMPLETED", "Completed"
        DISMISSED = "DISMISSED", "Dismissed"

    session = models.ForeignKey(
        NightlySession, on_delete=models.CASCADE, related_name="recommendations"
    )
    title = models.CharField(max_length=255)
    suggested_action = models.TextField()
    reasoning = models.TextField()
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # Supporting discoveries, projects, documents, or other context.
    evidence = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session", "status"]),
            models.Index(fields=["session", "priority"]),
        ]

    def __str__(self):
        return self.title


class RecommendationFeedback(models.Model):
    class FeedbackType(models.TextChoices):
        USEFUL = "USEFUL", "Useful"
        NOT_RELEVANT = "NOT_RELEVANT", "Not relevant"
        ALREADY_DONE = "ALREADY_DONE", "Already done"
        COMPLETED = "COMPLETED", "Completed"

    recommendation = models.ForeignKey(
        Recommendation, on_delete=models.CASCADE, related_name="feedback_entries"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recommendation_feedback",
    )
    feedback = models.CharField(max_length=20, choices=FeedbackType.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recommendation", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.recommendation_id} - {self.feedback}"


from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField


class VoiceBriefing(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="voice_briefings",
    )

    session = models.OneToOneField(
        "nightly_brain.NightlySession",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audio_briefing",
    )

    text = models.TextField()

    audio_url = CloudinaryField("file", resource_type="raw")

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Voice Briefing - {self.user} - {self.status}"


class MemoryContinuity(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memory_continuities",
    )

    session = models.OneToOneField(
        "nightly_brain.NightlySession",
        on_delete=models.CASCADE,
        related_name="memory_continuity",
    )

    summary = models.TextField(
        help_text="Generated memory continuity for this session."
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    error_message = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Memory continuity - {self.user_id} - {self.created_at}"

from datetime import timedelta
import tempfile

import cloudinary.uploader
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.document.models import DocumentChunk
from apps.nightly_brain.models import NightlySession, VoiceBriefing
from apps.nightly_brain.agent.discovery_agent import get_discover_agent
from apps.nightly_brain.agent.generate_summary import generate_summary
from apps.nightly_brain.agent.generate_voice import generate_speech
from django.core.cache import cache


User = get_user_model()


@shared_task(ignore_result=True)
def nightly_brain():
    now = timezone.now()
    yesterday = now - timedelta(days=1)

    users = User.objects.filter(
        document__chunks__created_at__gte=yesterday,
        document__chunks__created_at__lte=now,
    ).distinct()
    prefix_key = "today_users"
    cache.set(key=prefix_key,value=[user.id for user in users],timeout=60 * 60 * 8, )
    for user in users:
        
        

        chunks = DocumentChunk.objects.filter(
            document__user=user,
            created_at__gte=yesterday,
            created_at__lte=now,
        )

        if not chunks.exists():
            continue

        session = NightlySession.objects.create(
            user=user,
            status=NightlySession.Status.RUNNING,
            started_at=now,
        )

        briefing = VoiceBriefing.objects.create(
            user=user,
            text="",
            status=VoiceBriefing.Status.PENDING,
        )

        process_user_nightly_brain.delay(
            user.id,
            session.id,
            briefing.id,
        )


@shared_task(
    bind=True,
    ignore_result=True,
    max_retries=3,
)
def process_user_nightly_brain(self, user_id, session_id, briefing_id):
    session = NightlySession.objects.get(
        id=session_id,
        user_id=user_id,
    )
    briefing = VoiceBriefing.objects.get(
        id=briefing_id,
        user_id=user_id,
    )

    try:
        yesterday = timezone.now() - timedelta(days=1)

        chunks = DocumentChunk.objects.select_related(
            "document"
        ).filter(
            document__user_id=user_id,
            created_at__gte=yesterday,
        )

        chunks_data = [
            {
                "chunk_id": chunk.id,
                "document_title": chunk.document.title,
                "text": chunk.text,
            }
            for chunk in chunks
        ]

        if not chunks_data:
            session.status = NightlySession.Status.COMPLETED
            session.save(update_fields=["status"])
            return

        discover_agent = get_discover_agent()

        discoveries = discover_agent.invoke({
            "chunks": [item["text"] for item in chunks_data],
            "session": session,
        })

        

        summary_text = generate_summary(chunks_data)

        briefing.text = summary_text
        briefing.save(update_fields=["text", "updated_at"])

        audio_bytes = generate_speech(summary_text)

        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio.flush()

            upload_result = cloudinary.uploader.upload(
                temp_audio.name,
                resource_type="video",
                folder="voice_briefings",
            )




        briefing.audio_url = upload_result["secure_url"]
        briefing.status = VoiceBriefing.Status.COMPLETED
       
        briefing.error_message = None
        briefing.save(update_fields=[
            "audio_url",
            "status",
            "error_message",
            "updated_at",
        ])

        session.status = NightlySession.Status.COMPLETED
        session.save(update_fields=["status"])

    except Exception as exc:
        briefing.status = VoiceBriefing.Status.FAILED
        briefing.error_message = str(exc)
        briefing.save(update_fields=[
            "status",
            "error_message",
            "updated_at",
        ])

        session.status = NightlySession.Status.FAILED
        session.save(update_fields=["status"])

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)

        raise



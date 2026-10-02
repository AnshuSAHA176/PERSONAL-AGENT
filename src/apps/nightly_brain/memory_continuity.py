
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone

from .agent.memory_continuity_workflow import memery_containely_agent
from .models import VoiceBriefing, MemoryContinuity


@shared_task(bind=True, ignore_result=True)
def memory_worker(self):
    user_ids = cache.get("today_users", [])

    if not user_ids:
        return "No eligible users found."

    today = timezone.localdate()

    summaries = VoiceBriefing.objects.filter(
        user_id__in=user_ids,
        created_at__date=today,
    ).select_related("user", "session")

    memory_graph = memery_containely_agent()

    for briefing in summaries.iterator():
        try:
            result = memory_graph.invoke({
                "user_id": briefing.user_id,
                "summary": briefing.text,
                "related_chunks": [],
                "memory_summary": "",
            })

            memory_text = result["memory_summary"]

            MemoryContinuity.objects.update_or_create(
                session=briefing.session,
                defaults={
                    "user_id": briefing.user_id,
                    "summary": memory_text,
                    "status": MemoryContinuity.Status.COMPLETED,
                    "error_message": None,
                },
            )

        except Exception as exc:
            if briefing.session_id:
                MemoryContinuity.objects.update_or_create(
                    session_id=briefing.session_id,
                    defaults={
                        "user_id": briefing.user_id,
                        "summary": "",
                        "status": MemoryContinuity.Status.FAILED,
                        "error_message": str(exc),
                    },
                )
            else:
                self.retry(exc=exc, countdown=60, max_retries=3)

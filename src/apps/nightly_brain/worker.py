from celery import shared_task
from apps.document.models import DocumentChunk
from django.utils import timezone
from datetime import timedelta
from .agent.discovery_agent import get_discover_agent

@shared_task(bind=True, ignore_result=True)
def nightly_brain():

    yesterday = timezone.now() - timedelta(days=1)

    chunks = DocumentChunk.objects.select_related('document').filter(created_at=yesterday)

    if not chunks.exists():
        return 'yestarday no uploads'

    discovery_agent
    
    
    
    
    


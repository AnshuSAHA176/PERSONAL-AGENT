from celery import shared_task
from .models import Document
import requests



@shared_task(bind=True,ignore_result=True)
def DocumnetprocessWorker(self,instace_id):
        doc = Document.objects.filter(id = instace_id).first()
        if not doc:
                return

        try:
            pdf_url = doc.file.url.replace("http://", "https://")
            requests.get(url=doc.file.url,timeout=60)

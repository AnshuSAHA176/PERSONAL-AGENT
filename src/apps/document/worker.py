from celery import shared_task
from django.db import transaction

import requests
import tempfile
import os

from .models import Document, DocumentChunk
from .RAG import chunking, embedding, extract_text


@shared_task(bind=True, ignore_result=True)
def DocumentProcessWorker(self, instance_id):

    doc = Document.objects.filter(
        id=instance_id
    ).first()

    if not doc:
        return

    try:

        # -----------------------------------------
        # PROCESSING
        # -----------------------------------------

        doc.status = Document.Status.PROCESSING

        doc.save(
            update_fields=["status"]
        )

        # -----------------------------------------
        # DOWNLOAD FILE
        # -----------------------------------------

        response = requests.get(
            doc.file.url,
            timeout=60
        )

        response.raise_for_status()

        # -----------------------------------------
        # FILE FORMAT
        # -----------------------------------------

        file_format = os.path.splitext(
            doc.file.url.split("?")[0]
        )[1].lower()

        # -----------------------------------------
        # TEMPORARY FILE
        # -----------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=file_format
        ) as temp_file:

            temp_file.write(
                response.content
            )

            temp_file.flush()

            # -------------------------------------
            # EXTRACT TEXT
            # -------------------------------------

            documents = extract_text.extract_document(
                file_format=file_format,
                document_path=temp_file.name
            )

        # -----------------------------------------
        # CHUNKING
        # -----------------------------------------

        chunks = chunking.chunking(
            documents
        )

        # -----------------------------------------
        # CREATE CHUNKS
        # -----------------------------------------

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            embedding_vector = (
                embedding.generate_embedding(
                    chunk["text"]
                )
            )

            DocumentChunk.objects.create(

                document=doc,

                chunk_index=index,

                text=chunk["text"],

                embedding=embedding_vector,

                metadata={
                    "start": chunk["metadata_start"],
                    "end": chunk["metadata_end"],
                },

                token_count=len(
                    chunk["text"].split()
                )
            )

        # -----------------------------------------
        # READY
        # -----------------------------------------

        doc.status = Document.Status.READY

        doc.save(
            update_fields=["status"]
        )

    except Exception as e:

        doc.status = Document.Status.FAILED

        doc.save(
            update_fields=["status"]
        )

        raise
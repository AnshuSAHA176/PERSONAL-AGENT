from django.db import models
from cloudinary.models import CloudinaryField


class Document(models.Model):


    class Status(models.TextChoices):
        PENDING = "PENDING","pending"
        PROCESSING = "PROCESSING","processing"
        READY = "READY" , "ready"
        FAILED ="FAILED" ,"failed"



    title = models.CharField(max_length=300)
    user = models.ForeignKey('account.User',on_delete=models.CASCADE,related_name='documents')
    file = CloudinaryField("file", resource_type="raw")
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=200)
    uploaded = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default=Status.PENDING,choices=Status.choices)

    class Meta:
        indexes = [
        
            models.Index(fields=['title']),
            
          
            models.Index(fields=['uploaded']),
        ]
    def __str__(self):
        return f'Title :- {self.title}'


from django.db import models
from pgvector.django import VectorField


class DocumentChunk(models.Model):

    document = models.ForeignKey(
        "document.Document",
        on_delete=models.CASCADE,
        related_name="chunks"
    )

    chunk_index = models.PositiveIntegerField()

    text = models.TextField()

    embedding = VectorField(
        dimensions=1024
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    token_count = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["chunk_index"]

        constraints = [
            models.UniqueConstraint(
                fields=["document", "chunk_index"],
                name="unique_document_chunk"
            )
        ]

        indexes = [
            models.Index(
                fields=["document", "chunk_index"],
                name="document_chunk_idx"
            )
        ]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
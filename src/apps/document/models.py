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
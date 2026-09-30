from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializer import DocumentSerializer
from .models import Document


class DocumentView(viewsets.ModelViewSet):
    permission_classes =[IsAuthenticated]
    serializer_class = DocumentSerializer



   

    def get_queryset(self):
        return Document.objects.select_related('user').filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
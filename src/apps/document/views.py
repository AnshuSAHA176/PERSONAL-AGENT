from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializer import DocumentSerializer, SimilarChunksSerializer
from .models import Document, DocumentChunk
from rest_framework.views import APIView
from pgvector.django import CosineDistance
from .RAG.embedding import generate_embedding
from rest_framework.response import Response
from rest_framework import status


class DocumentView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.select_related("user").filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class SimilarityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if not data:
            return Response(
                {"errr": "Please provide a valid responce"},
                status=status.HTTP_400_BAD_REQUEST,
            )


        embedding = generate_embedding(text=data)
        document_chunks = DocumentChunk.objects.filter(
            document__user=request.user
        ).annotate(distance=CosineDistance("embedding",embedding)).order_by("distance")[:4]

        return Response(SimilarChunksSerializer(document_chunks,many=True).data)
from rest_framework import serializers

from .models import Document, DocumentChunk
from .worker import DocumentProcessWorker


class DocumentSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "email",
            "file",
            "file_size",
            "mime_type",
            "uploaded",
            "status",
        ]

        extra_kwargs = {
            "user": {"read_only": True},
            "file_size": {"read_only": True},
            "mime_type": {"read_only": True},
            "status": {"read_only": True},
        }

    def validate(self, attrs):
        if not attrs["title"]:
            raise serializers.ValidationError("Please provide a title")
        if not attrs["file"]:
            raise serializers.ValidationError("file is required")
        return attrs

    def create(self, validated_data):
        file = validated_data["file"]
        validated_data["file_size"] = file.size
        validated_data["mime_type"] = file.content_type
        documment = Document.objects.create(**validated_data)
        DocumentProcessWorker.delay(documment.id)
        return documment


class SimilarChunksSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ["document", "text", "metadata", "created_at"]
    
class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = [ "metadata"]

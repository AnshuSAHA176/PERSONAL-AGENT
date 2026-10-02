from rest_framework import serializers
from .models import VoiceBriefing,NightlySession, Discovery


class BrifingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceBriefing
        fields = "__all__"





class DiscoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Discovery
        fields = [
            "id",
            "discovery_type",
            "title",
            "description",
            "source_references",
            "metadata",
            "created_at",
        ]


class NightlySessionSerializer(serializers.ModelSerializer):
    discoveries = DiscoverySerializer(many=True, read_only=True)

    class Meta:
        model = NightlySession
        fields = [
            "id",
            "status",
            "started_at",
            "completed_at",
            "error_message",
            "discoveries",
        ]
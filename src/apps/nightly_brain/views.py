# views.py

from rest_framework.generics import ListAPIView


from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NightlySession, Discovery,VoiceBriefing
from .serializers import (
    NightlySessionSerializer,
    DiscoverySerializer,
    BrifingSerializer
)
from .tasks import nightly_brain



class BriefingListView(ListAPIView):
    serializer_class = BrifingSerializer

    def get_queryset(self):
        return VoiceBriefing.objects.filter(
            user=self.request.user
        ).order_by("-created_at")




class NightlySessionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NightlySessionSerializer

    def get_queryset(self):
        return NightlySession.objects.filter(
            user=self.request.user
        )


class NightlySessionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NightlySessionSerializer

    def get_queryset(self):
        return NightlySession.objects.filter(
            user=self.request.user
        )


class SessionDiscoveryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiscoverySerializer

    def get_queryset(self):
        return Discovery.objects.filter(
            session__user=self.request.user,
            session_id=self.kwargs["session_id"],
        )


class DiscoveryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiscoverySerializer

    def get_queryset(self):
        return Discovery.objects.filter(
            session__user=self.request.user
        )


class TriggerNightlyBrainView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        task = nightly_brain.delay()

        return Response({
            "message": "Nightly Brain task queued.",
            "task_id": task.id,
        }, status=202)
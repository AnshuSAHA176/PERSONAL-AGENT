from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    DocumnetSerializer,
    VoiceSerializer,
)
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.views import APIView
from apps.document.models import Document
from apps.nightly_brain.models import NightlySession, VoiceBriefing
from django.db.models import Count, Q
from django.core.cache import cache


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = super().post(request, *args, **kwargs)
        except IntegrityError:

            return Response(
                {"error": "A user with this email already exits"},
                status=status.HTTP_409_CONFLICT,
            )

        return user


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        refresh = RefreshToken.for_user(user=user)
        access = refresh.access_token

        return Response(
            {"access": str(access), "refresh": str(refresh)}, status=status.HTTP_200_OK
        )


class DashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefix = f"dashboard-{request.user.id}"
        cache_data = cache.get(prefix)
        if cache_data:
            return Response(cache_data)

        documents = Document.objects.filter(user=request.user).order_by('-uploaded')
        total_documents = documents.count()
        
        
        seasion = NightlySession.objects.filter(
            user=request.user, status=NightlySession.Status.COMPLETED
        ).aggregate(
            completed_sessions=Count("id"),
            memory_records=Count("memory_continuity"),
            audio_briefings=Count("audio_briefing"),
        )
        latest_audio = (
            VoiceBriefing.objects.filter(
                user=request.user, status=VoiceBriefing.Status.COMPLETED
            )
            .order_by("-created_at")
            .first()
        )

        data = {
            "stats": {"total_documents": total_documents, "seasion": seasion},
            "recent_documents": DocumnetSerializer(documents[:5], many=True).data,
            "latest_briefing": VoiceSerializer(latest_audio).data,
        }

        cache.set(key=prefix, value=data, timeout=60 * 60)

        return Response(data)

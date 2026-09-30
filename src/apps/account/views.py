from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User
from .serializer import RegisterSerializer,LoginSerializer
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.views import APIView



class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            user =super().post(request, *args, **kwargs)
        except IntegrityError:

            return Response({
                "error":"A user with this email already exits"
            },status=status.HTTP_409_CONFLICT)
        
        return user


class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        refresh = RefreshToken.for_user(user=user)
        access = refresh.access_token

        return Response({
            "access" :str(access),
            "refresh":str(refresh)
        },status=status.HTTP_200_OK)
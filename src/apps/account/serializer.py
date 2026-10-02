from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from apps.document.models import Document
from apps.nightly_brain.models import VoiceBriefing

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password"
        ]

        extra_kwargs ={
            "password":{
                "write_only" : True,
                
            }
        }

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)


    def validate(self, attrs):
        
        user = authenticate(email = attrs['email'],password = attrs['password'])
        if not user:
            raise serializers.ValidationError('Please enter a valid email & password')

        attrs['user'] = user

        return attrs

class DocumnetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields =[
            'title',
            'uploaded',
            'status'
        ]
class VoiceSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = VoiceBriefing
        fields = ["id", "title", "audio_url", "status"]

    def get_title(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
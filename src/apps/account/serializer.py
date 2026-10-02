from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from apps.document.models import Document


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
            'title'
'uploaded'
'status'
        ]
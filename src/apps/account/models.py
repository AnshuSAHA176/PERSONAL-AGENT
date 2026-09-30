from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from .customemanager import MyUserManager
from django.contrib.auth.models import PermissionsMixin



class User(AbstractBaseUser,PermissionsMixin):
    objects = MyUserManager()
    username = None
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    

    USERNAME_FIELD = "email"
    
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    
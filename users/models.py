from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    username = models.CharField(max_length=150)
    
    email = models.EmailField(unique=True)

    oauth_provider = models.CharField(max_length=50)
    oauth_id = models.CharField(max_length=255)

    profile_picture = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
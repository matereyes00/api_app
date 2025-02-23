from django.db import models
from django import forms

from django.contrib.auth.models import User  # Import the User model
from django.contrib.postgres.fields import ArrayField  # Use for lists


# User's profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    watchlist = models.JSONField(default=dict)  # Stores movies, books, and games

    def __str__(self):
        return self.user.username

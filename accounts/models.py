from django.db import models
from django import forms

from django.contrib.auth.models import User  # Import the User model


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # username = models.CharField(max_length=150, blank=False, null=False)
    # password = models.CharField(max_length=150, blank=False, null=False)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='default.jpg')  # Make sure this line is present

    def __str__(self):
        return self.user.username
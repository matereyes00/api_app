from django.db import models
from django.contrib.auth.models import User  # Import the User model


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='default.jpg')  # Make sure this line is present
    # ... other fields

    def __str__(self):
        return self.user.username
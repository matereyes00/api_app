from django.db import models
from django import forms

from django.contrib.auth.models import User  # Import the User model

# User's profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


# has user seen the movie
class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    imdb_id = models.CharField(max_length=20)  # Store OMDb API's imdbID
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'imdb_id')  # Ensure no duplicates

    def __str__(self):
        return f"{self.user.username} watched {self.imdb_id}"

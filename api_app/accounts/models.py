from django.db import models
from django import forms

from django.contrib.auth.models import User  # Import the User model
from django.contrib.postgres.fields import ArrayField  # Use for lists
from django.utils.timezone import now


class CustomList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customList")
    custom_list_id = models.BigAutoField(primary_key=True)
    list_name = models.CharField(max_length=255) 
    list_description = models.TextField(default="", blank=True)
    item_id = models.CharField(max_length=255)  # Unique ID for the favorite item (IMDB ID, OLID, etc.)
    date_added = models.DateTimeField(default=now)  # ✅ Correct way


# User's profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="", blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', 
        blank=True, 
        null=True
    )
    watchlist_past = models.JSONField(default=dict)  # Stores movies, books, and games
    custom_lists = models.ManyToManyField(CustomList)
    
    def __str__(self):
        return self.user.username
    
class PastWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="past_watchlist")
    category = models.CharField(max_length=20, choices=[
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
        ('book', 'Book'),
        ('boardgame', 'Board Game'),
        ('videogame', 'Video Game')
    ])
    item_id = models.CharField(max_length=255)  # Store OLID, IMDbID, Game ID
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp for sorting/filtering
    
    class Meta:
        unique_together = ('user', 'category', 'item_id')  # Prevent duplicate entries

    def __str__(self):
        return f"Past Watchlist for {self.user.username} - {self.category}: {self.item_id}"

class FutureWatchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="future_watchlist")
    category = models.CharField(max_length=20, choices=[
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
        ('book', 'Book'),
        ('boardgame', 'Board Game'),
        ('videogame', 'Video Game')
    ])
    item_id = models.CharField(max_length=255)  # Store OLID, IMDbID, Game ID
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp for sorting/filtering
    
    class Meta:
        unique_together = ('user', 'category', 'item_id')  # Prevent duplicate entries

    def __str__(self):
        return f"Future watchlist for: {self.user.username} - {self.category}: {self.item_id}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    category = models.CharField(max_length=20, choices=[
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
        ('book', 'Book'),
        ('boardgame', 'Board Game'),
        ('videogame', 'Video Game')
    ])
    item_id = models.CharField(max_length=255)  # Unique ID for the favorite item (IMDB ID, OLID, etc.)
    date_added = models.DateTimeField(default=now)  # ✅ Correct way
    

    def __str__(self):
        return f"{self.user.username} - {self.category}: {self.item_id}"

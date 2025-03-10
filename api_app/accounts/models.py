from django.db import models
from django import forms

from django.contrib.auth.models import User  # Import the User model
from django.contrib.postgres.fields import ArrayField  # Use for lists
from django.utils.timezone import now
from django.core.exceptions import ValidationError

from get import fetch_media_info
from api_app.lists.models import CustomList

# User's profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="", blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', 
        blank=True, 
        null=True
    )
    watchlist_past = models.JSONField(default=dict)  # Stores movies, books, and games
    custom_lists = models.ManyToManyField(CustomList, blank=True)
    
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
    title = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp for sorting/filtering

    class Meta:
        unique_together = ('user', 'category', 'item_id')  # Prevent duplicate entries

    def __str__(self):
        return f"Future watchlist for: {self.user.username} - {self.category}: {self.title or self.item_id}"

    def save(self, *args, **kwargs):
        if not self.title or not self.year or not self.image:  # Only fetch if missing
            self.update_media_info()
        super().save(*args, **kwargs)

    def update_media_info(self):
        """Fetch and update media info from API without calling save()."""
        data = fetch_media_info(self.category, self.item_id)
        if data:
            self.title = data.get("title") or data.get("Title") or data.get("name")
            self.year = data.get("Year") or data.get("yearpublished") or data.get("first_publish_date")
            self.description = data.get("Plot") or data.get("description")
            self.image = data.get("image") or data.get("Poster") or data.get("cover_url")

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
    title = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)  # Timestamp for sorting/filtering

    class Meta:
        unique_together = ('user', 'category', 'item_id')  # Prevent duplicate entries

    def __str__(self):
        return f"Future watchlist for: {self.user.username} - {self.category}: {self.title or self.item_id}"

    def save(self, *args, **kwargs):
        if not self.title or not self.year or not self.image:  # Only fetch if missing
            self.update_media_info()
        super().save(*args, **kwargs)

    def update_media_info(self):
        """Fetch and update media info from API."""
        data = fetch_media_info(self.category, self.item_id)
        if data:
            self.title = data.get("title") or data.get("Title") or data.get("name")
            self.year = data.get("Year") or data.get("yearpublished") or data.get("first_publish_date")
            self.description = data.get("Plot") or data.get("description")
            self.image = data.get("image") or data.get("Poster") or data.get("cover_url")
            self.save()

class Favorite(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="favorites")
    category = models.CharField(max_length=50, choices=[
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
        ('book', 'Book'),
        ('boardgame', 'Board Game'),
        ('videogame', 'Video Game')
    ])
    item_id = models.CharField(max_length=255)  # External API ID
    title = models.CharField(max_length=500, blank=True, null=True)
    year = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'item_id')  # Prevent duplicate favorites
        ordering = ['-date_added']  # Show newest first

    def save(self, *args, **kwargs):
        """Fetch and store title, year, description, and image when saving."""
        if not self.title or not self.year or not self.image:  # Fetch only if missing
            data = fetch_media_info(self.category, self.item_id)
            if data:
                self.title = data.get("title") or data.get("Title") or data.get("name", "Unknown")
                self.year = data.get("Year") or data.get("yearpublished") or data.get("first_publish_date", "N/A")
                self.description = data.get("Plot") or data.get("description", "No description available.")
                self.image = data.get("image") or data.get("Poster") or data.get("cover_url", "")

        super().save(*args, **kwargs)  # Save to the database

    def __str__(self):
        return self.title or "Unknown Favorite"
    
class FourFavorite(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="four_favorites")
    category = models.CharField(max_length=50, choices=[
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
        ('book', 'Book'),
        ('boardgame', 'Board Game'),
        ('videogame', 'Video Game')
    ])
    item_id = models.CharField(max_length=255)  # External API ID
    title = models.CharField(max_length=500, blank=True, null=True)
    year = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'item_id')  # Prevent duplicate favorites
        ordering = ['-date_added']  # Show newest first

    def save(self, *args, **kwargs):
        if FourFavorite.objects.filter(user=self.user).count() >= 4:  # 🔴 This enforces the limit
            raise ValidationError("Too many records mate")  # 👈 This is where your error is coming from
        """Fetch and store title, year, description, and image when saving."""
        if not self.title or not self.year or not self.image:  # Fetch only if missing
            data = fetch_media_info(self.category, self.item_id)
            if data:
                self.title = data.get("title") or data.get("Title") or data.get("name", "Unknown")
                self.year = data.get("Year") or data.get("yearpublished") or data.get("first_publish_date", "N/A")
                self.description = data.get("Plot") or data.get("description", "No description available.")
                self.image = data.get("image") or data.get("Poster") or data.get("cover_url", "")

        super().save(*args, **kwargs)  # Save to the database

    def __str__(self):
        return self.title or "Unknown Favorite"
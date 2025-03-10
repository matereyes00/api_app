from django.db import models
from django.contrib.auth.models import User
from get import fetch_media_info
from api_app.accounts.models import User
from django.utils.timezone import now


class CustomList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customList")
    custom_list_id = models.BigAutoField(primary_key=True)
    list_name = models.CharField(max_length=255) 
    list_description = models.TextField(default="", blank=True)
    date_added = models.DateTimeField(default=now)  # ✅ Correct way

# Create your models here.
class CustomListItem(models.Model):
    custom_list_id = models.ForeignKey(CustomList, on_delete=models.CASCADE, related_name="customList")
    category = models.CharField(max_length=20, choices=[
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
    image_url = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('custom_list_id', 'category', 'item_id')  # Prevent duplicate favorites
        ordering = ['-date_added']  # Show newest first

    def save(self, *args, **kwargs):
        """Fetch and store title, year, description, and image when saving."""
        if not self.title or not self.year or not self.image_url:  # Fetch only if missing
            data = fetch_media_info(self.category, self.item_id)
            if data:
                self.title = data.get("title") or data.get("Title") or data.get("name", "Unknown")
                self.year = data.get("Year") or data.get("yearpublished") or data.get("first_publish_date", "N/A")
                self.description = data.get("Plot") or data.get("description", "No description available.")
                self.image = data.get("image") or data.get("Poster") or data.get("cover_url", "")

        super().save(*args, **kwargs)  # Save to the database

    def __str__(self):
        return self.title or "Unknown Media Item"



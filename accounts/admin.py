from django.contrib import admin
from .models import Profile, Favorite


# Register your models here.
import json

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "formatted_watchlist")

    def formatted_watchlist(self, obj):
        return json.dumps(obj.watchlist_past, indent=2) if obj.watchlist_past else "No Watchlist"

    formatted_watchlist.short_description = "Watchlist (Formatted)"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Favorite)
from django.contrib import admin
from .models import Profile


# Register your models here.
import json

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "formatted_watchlist")

    def formatted_watchlist(self, obj):
        return json.dumps(obj.watchlist, indent=2) if obj.watchlist else "No Watchlist"

    formatted_watchlist.short_description = "Watchlist (Formatted)"


admin.site.register(Profile, ProfileAdmin)

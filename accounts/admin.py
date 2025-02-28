from django.contrib import admin
from django.utils.safestring import mark_safe
import json
from .models import Profile, Favorite

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "formatted_watchlist")

    def formatted_watchlist(self, obj):
        """Formats JSON data with indentation and wraps it in <pre> for better readability."""
        if not obj.watchlist_past:
            return "No Watchlist"
        formatted_json = json.dumps(obj.watchlist_past, indent=2)  # Pretty-print JSON
        return mark_safe(f"<pre>{formatted_json}</pre>")  # Preserve formatting in admin UI

    formatted_watchlist.short_description = "Watchlist (Formatted)"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Favorite)

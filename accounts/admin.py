from django.contrib import admin
from django.utils.safestring import mark_safe
import json
from .models import Profile, Favorite, FutureWatchlist
from .get import get_bgg_game_info, get_bgg_game_type,get_movietv_info,get_book_info

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "formatted_watchlist")

    def formatted_watchlist(self, obj):
        """Formats JSON data with indentation and wraps it in <pre> for better readability."""
        if not obj.watchlist_past:
            return "No Watchlist"
        formatted_json = json.dumps(obj.watchlist_past, indent=2)  # Pretty-print JSON
        return mark_safe(f"<pre>{formatted_json}</pre>")  # Preserve formatting in admin UI

    formatted_watchlist.short_description = "Watchlist (Formatted)"


def get_item_name(category, item_id):
    if category == "book":
        return get_book_info(item_id)  # Replace with actual API function
    elif category == "movie" or category == 'tv':
        return get_movietv_info(item_id)
    elif category == "boardgame" or category == 'videogame':
        return get_bgg_game_info(item_id)
    return "Unknown"


class FutureWatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "item_id", "item_name", "date_added")
    list_filter = ("category", "date_added")  
    search_fields = ("user__username", "item_id")  
    ordering = ("-date_added",)  
    def item_name(self, obj):
        return get_item_name(obj.category, obj.item_id)  
    item_name.short_description = "Item Name"  

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Favorite)
admin.site.register(FutureWatchlist, FutureWatchlistAdmin)

from django.contrib import admin
from django.utils.safestring import mark_safe
import json
from .models import Profile, Favorite, FutureWatchlist, CustomList
from .templates.API_.get import get_bgg_game_info, get_bgg_game_type,get_movietv_info,get_book_info

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
    list_display = ('user', 'category', 'item_id', 'date_added')  # Columns to show in the list view
    list_filter = ('category', 'date_added')  # Filters on the right sidebar
    search_fields = ('user__username', 'item_id')  # Search by username or item ID
    ordering = ('-date_added',)  # Sort by most recently added first
    date_hierarchy = 'date_added'  # Adds a date filter at the top
    list_per_page = 20  # Pagination

    fieldsets = (
        ("User Info", {"fields": ("user",)}),
        ("Item Details", {"fields": ("category", "item_id")}),
        ("Timestamps", {"fields": ("date_added",)}),
    )

    readonly_fields = ("date_added",)  # Prevents modification of auto-generated timestamps

class CustomWatchlistAdmin(admin.ModelAdmin):
    list_display = ('list_name', 'list_description', 'user', 'custom_list_id', 'date_added')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Favorite)
admin.site.register(FutureWatchlist, FutureWatchlistAdmin)
admin.site.register(CustomList, CustomWatchlistAdmin)

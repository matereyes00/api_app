from django.contrib import admin
from django.utils.safestring import mark_safe
import json
from django.utils.html import format_html
from .models import Profile, Favorite, FutureWatchlist, CustomList, FourFavorite
from get import get_bgg_game_info, get_bgg_game_type,get_movietv_info,get_book_info, fetch_media_info

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
    list_display = ('user', 'category', 'title', 'year', 'date_added')  # Show title and year
    list_filter = ('category', 'date_added')  
    search_fields = ('user__username', 'item_id', 'title')  
    ordering = ('-date_added',)  
    date_hierarchy = 'date_added'  
    list_per_page = 20  

    fieldsets = (
        ("User Info", {"fields": ("user",)}),
        ("Item Details", {"fields": ("category", "item_id", "title", "year", "description", "image")}),
        ("Timestamps", {"fields": ("date_added",)}),
    )

    readonly_fields = ("date_added",)  # Prevents modification of timestamps


class CustomWatchlistAdmin(admin.ModelAdmin):
    list_display = ('list_name', 'list_description', 'user', 'custom_list_id', 'date_added')
    

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'title', 'year', 'date_added')  # Show title & year
    list_filter = ('category', 'date_added')  
    search_fields = ('user__username', 'title', 'item_id')  
    ordering = ('-date_added',)  
    date_hierarchy = 'date_added'  
    list_per_page = 20  

    fieldsets = (
        ("User Info", {"fields": ("user",)}),
        ("Item Details", {"fields": ("category", "item_id", "title", "year", "description", "image_url")}),
        ("Timestamps", {"fields": ("date_added",)}),
    )
    
    def get_image(self):
        """Fetch and display image dynamically."""
        data = fetch_media_info(self.category, self.item_id)
        image_url = data.get("image") or data.get("Poster") or data.get("cover_url")
        return image_url if image_url else "No Image"
    readonly_fields = ("date_added",)  # Prevents modification of timestamps


class FourFavoritesAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "category", "year", "item_id", "image_preview")  # 👈 Display columns
    search_fields = ("title", "category", "year", "item_id")  # 🔎 Allow searching

    def image_preview(self, obj):
        """Display image preview in the admin panel."""
        if obj.image_url:
            return mark_safe(f'<img src="{obj.image_url}" width="50" height="50" style="border-radius: 5px;" />')
        return "No Image"

    image_preview.short_description = "Image"

admin.site.register(Profile, ProfileAdmin)
admin.site.register(FutureWatchlist, FutureWatchlistAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(FourFavorite, FourFavoritesAdmin)
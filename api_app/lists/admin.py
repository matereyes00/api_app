from django.contrib import admin

# Register your models here.
from .models import CustomList, CustomListItem

class CustomListItemInline(admin.TabularInline):
    model = CustomListItem
    extra = 1  # Allows adding list items directly within a CustomList

class CustomListAdmin(admin.ModelAdmin):
    list_display = ("list_name", "user", "date_added")  # Columns in the admin list view
    search_fields = ("list_name", "user__username")  # Searchable fields
    list_filter = ("date_added",)  # Filter by date
    inlines = [CustomListItemInline]  # Show list items inline when viewing a CustomList

class CustomListItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "custom_list_id", "date_added")  # Admin columns
    search_fields = ("title", "category", "custom_list_id__list_name")  # Search by title or list name
    list_filter = ("category", "date_added")  # Filters for easy navigation

admin.site.register(CustomListItem, CustomListItemAdmin)
admin.site.register(CustomList, CustomListAdmin)

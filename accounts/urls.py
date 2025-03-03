# accounts/urls.py
from django.urls import path

from . import views as v 

app_name = 'accounts'  # Corrected namespace

urlpatterns = [
    path("register/", v.RegisterView.as_view(), name="register"),
    path('profile/', v.profile_view, name='profile'),
    path('edit_profile/', v.edit_profile, name='edit_profile'),
    path("add_to_watchlist/<str:category>/<str:item_id>/", 
        v.add_to_consumed_media, name="add_to_watchlist"),
    path("remove/<str:category>/<str:item_id>/", 
        v.remove_from_consumed_media, name="remove_from_watchlist"),
    path("add_to_favorites/<str:category>/<str:item_id>/", 
        v.add_to_favorites, name="add_to_favorites"),
    path('add_to_future_watchlist/<str:category>/<str:item_id>/', v.add_to_future_watchlist, name='add_to_future_watchlist'),
    path('remove_from_future_watchlist/<str:category>/<str:item_id>/', v.remove_from_future_watchlist, name='remove_from_future_watchlist'),
    path('remove_from_favorites/<str:category>/<str:item_id>/', v.remove_from_favorites, name="remove_from_favorites"),
]
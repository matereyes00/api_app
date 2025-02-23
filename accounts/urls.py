# accounts/urls.py
from django.urls import path

from. import views as v

app_name = 'accounts'  # Corrected namespace

urlpatterns = [
    path("register/", v.RegisterView.as_view(), name="register"),
    path('profile/', v.profile_view, name='profile'),
    path('profile/edit_profile/', v.edit_profile, name='edit_profile'),

    path("add_to_watchlist/<str:item_type>/<str:item_id>/", v.add_to_watchlist, name="add_to_watchlist"),

]
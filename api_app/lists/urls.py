# accounts/urls.py
from django.urls import path

from . import views as v 

app_name = 'lists'  # Corrected namespace

urlpatterns = [
    path('create_watchlist/', v.create_custom_watchlist, name="create_watchlist"),
]
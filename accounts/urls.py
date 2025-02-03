# accounts/urls.py
from django.urls import path

from. import views as v

app_name = 'accounts'  # Corrected namespace

urlpatterns = [
    path("register/", v.RegisterView.as_view(), name="register"),
    path('profile/', v.profile_view, name='profile'),
]
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash  # Keeps user logged in
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

from common.API.get import get_bgg_game_info,get_movietv_info,get_book_info, get_movietv_data_using_imdbID, get_media_category, fetch_media_info
from common.API.deleteFromList import delete_future_watchlist_item, delete_favorite_item, delete_past_watchlist_item

from api_app.accounts.models import Favorite, FutureWatchlist, FourFavorite, PastWatchlist
from api_app.lists.models import CustomList
from.forms import CustomUserCreationForm, ProfileUpdateForm

import json
import requests
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env
api_key = os.getenv('OMDB_API_KEY')


class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # Use the custom form
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

@login_required
def profile_view(request):
    category = request.GET.get("category")  # Example: 'books', 'games', etc.
    item_id = request.GET.get("item_id")  # ID for API request
    item_data = None  
    profile = request.user.profile 

    past_watchlist = PastWatchlist.objects.filter(user=request.user)
    four_favorites = FourFavorite.objects.filter(user=request.user)
    future_watchlist = FutureWatchlist.objects.filter(user=request.user)
    favorites = Favorite.objects.filter(user=request.user)
    custom_lists = CustomList.objects.filter(user=request.user)
    
    # get_media_info so that when u click on the link (from the profile), youll see the info
    

    return render(request, "Profile/profile.html", {
        "profile": profile,
        "past_watchlist": past_watchlist,
        "future_watchlist": future_watchlist,
        "favorites": favorites,
        "custom_lists": custom_lists,
        "category": category,
        "item_id":item_id,
        "item_data": item_data,
        "four_favorites":four_favorites,
    })


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        password_form = PasswordChangeForm(request.user, request.POST)  # Password form
        if profile_form.is_valid():
            profile_form.save()
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Prevents logout after password change
        return redirect('api_app.accounts:profile')  # Redirect after form submission
    else:
        profile_form = ProfileUpdateForm(instance=profile)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'profile/editProfile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })


@login_required
def profile_activity(request, activity):
    context = {}
    favorites = Favorite.objects.filter(user=request.user)
    future_watchlist = FutureWatchlist.objects.filter(user=request.user)
    custom_watchlist = CustomList.objects.filter(user=request.user)
    past_watchlist = PastWatchlist.objects.filter(user=request.user)
    query_results = None
    query = request.GET.get('query')
    clear_query = request.GET.get('clear-search-result')
    if clear_query:
        query.delete()
    
    if query:
        if activity == 'favorites':
            query_results=Favorite.objects.filter(title__icontains=query)
        if activity == 'past_watchlist':
            query_results=PastWatchlist.objects.filter(title__icontains=query)
        if activity == 'future_watchlist':
            query_results=FutureWatchlist.objects.filter(title__icontains=query)
        if activity == 'custom_watchlists':
            query_results=CustomList.objects.filter(title__icontains=query)
    
    template = 'Profile/baseActivityView.html'
    context = {
            'future_watchlist': future_watchlist,
            'custom_watchlists': custom_watchlist,
            'past_watchlist': past_watchlist,
            'favorites':favorites,
            'activity':activity,
            'query': query,
            'query_results': query_results,
        }
    return render(request, template, context)

@login_required
def remove_from_consumed_media(request, category, item_id):
    past_watchlist = PastWatchlist.objects.filter(user=request.user) 
    if request.method == 'POST':
        category_ = get_media_category(category, item_id)
        media_data = fetch_media_info(category_, item_id)  # Fetch media info
        delete_past_watchlist_item(request, (media_data['imdbID'] or media_data['olid'] or media_data['gameID']), category_)

        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def add_to_consumed_media(request, category, item_id):
    if request.method == "POST":
        category_ = get_media_category(category, item_id)
        media_data = fetch_media_info(category_, item_id)  # Fetch media info
        PastWatchlist.objects.get_or_create(
            user=request.user,
            category=category_,
            item_id=item_id,
            defaults={
                "title": media_data.get("title") or media_data.get("Title") or media_data.get("name"),
                "year": media_data.get("Year") or media_data.get("yearpublished") or media_data.get("first_publish_date"),
                "description": media_data.get("Plot") or media_data.get("description"),
                "image": media_data.get("image") or media_data.get("Poster") or media_data.get("cover_url"),
            }
        )
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_to_future_watchlist(request, category, item_id):
    if request.method == "POST":
        category_ = get_media_category(category, item_id)
        media_data = fetch_media_info(category_, item_id)  # Fetch media info
        FutureWatchlist.objects.get_or_create(
            user=request.user,
            category=category_,
            item_id=item_id,
            defaults={
                "title": media_data.get("title") or media_data.get("Title") or media_data.get("name"),
                "year": media_data.get("Year") or media_data.get("yearpublished") or media_data.get("first_publish_date"),
                "description": media_data.get("Plot") or media_data.get("description"),
                "image": media_data.get("image") or media_data.get("Poster") or media_data.get("cover_url"),
            }
        )
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def remove_from_future_watchlist(request, category, item_id):
    if request.method == "POST":
        future_watchlist = FutureWatchlist.objects.filter(user=request.user) 
        category_ = get_media_category(category, item_id)
        media_data = fetch_media_info(category_, item_id)  # Fetch media info
        delete_future_watchlist_item(request, (media_data['imdbID'] or media_data['olid'] or media_data['gameID']), category_)
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def add_to_favorites(request, category, item_id):
    if request.method == 'POST':
        category_ = get_media_category(category, item_id)
        media_data = fetch_media_info(category_, item_id)  # Fetch media info
        Favorite.objects.get_or_create(
            user=request.user,
            category=category_,
            item_id=item_id,
            defaults={
                "title": media_data.get("title") or media_data.get("Title") or media_data.get("name"),
                "year": media_data.get("Year") or media_data.get("yearpublished") or media_data.get("first_publish_date"),
                "description": media_data.get("Plot") or media_data.get("description"),
                "image": media_data.get("image") or media_data.get("Poster") or media_data.get("cover_url"),
            }
        )
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def remove_from_favorites(request, category, item_id):
    if request.method == 'POST':
        category_ = get_media_category(category, item_id)
        media_data = fetch_media_info(category_, item_id)  # Fetch media info
        delete_favorite_item(request, (media_data['imdbID'] or media_data['olid'] or media_data['gameID']), category_)
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def add_to_four_favorites(request, category, item_id):
    if request.method == 'POST':
        category_ = get_media_category(category, item_id)
        try:
            if FourFavorite.objects.filter(user=request.user).count() >= 4:
                raise ValidationError("Too many records mate")  # Raise the same validation error

            media_data = fetch_media_info(category_, item_id)
            FourFavorite.objects.get_or_create(
                user=request.user,
                category=category_,
                item_id=item_id,
                defaults={"title": media_data.get("title", ""), "year": media_data.get("year", ""),
                        "description": media_data.get("description", ""), "image": media_data.get("image", "")}
            )

        except ValidationError as e:
            messages.error(request, str(e))  # Store error message in session

        return redirect(request.META.get("HTTP_REFERER", "/"))  # Redirect to the same page
    return redirect("/")  # Fallback in case of non-POST request
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
from common.API.deleteFromList import delete_future_watchlist_item, delete_favorite_item

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

    # Ensure watchlist_past is correctly formatted
    if not profile.watchlist_past or not isinstance(profile.watchlist_past, dict):
        profile.watchlist_past = {"movies": [], "games": [], "books": [], "tv": [], "video_games": []}
    if isinstance(profile.watchlist_past, str):
        profile.watchlist_past = json.loads(profile.watchlist_past)

    past_watchlist = profile.watchlist_past
    four_favorites = FourFavorite.objects.filter(user=request.user)
    future_watchlist = FutureWatchlist.objects.filter(user=request.user)
    
    # get_media_info so that when u click on the link (from the profile), youll see the info
    

    return render(request, "Profile/profile.html", {
        "profile": profile,
        "watchlist": past_watchlist,
        "future_watchlist": future_watchlist,
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
    profile = request.user.profile 
    favorites = Favorite.objects.filter(user=request.user)
    future_watchlist = FutureWatchlist.objects.filter(user=request.user)
    custom_watchlist = CustomList.objects.filter(user=request.user)
    past_watchlist = PastWatchlist.objects.filter(user=request.user)
    
    for item in Favorite.objects.all():
        item.save() 
    
    template = 'Profile/baseActivityView.html'
    
    context = {
            'future_watchlist': future_watchlist,
            'custom_watchlists': custom_watchlist,
            'past_watchlist': past_watchlist,
            'favorites':favorites,
        }
    return render(request, template, context)


''' TO DO: SEPARATE PASTWATCHLIST field from PROFILE model '''
@login_required
def remove_from_consumed_media(request, category, item_id):
    profile = request.user.profile
    watchlist = profile.watchlist_past 
    if request.method == 'POST':
        if not watchlist or not isinstance(watchlist, dict):
            watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games": []}
        
        if category == 'books':
            book_data = get_book_info(item_id)
            watchlist['books'] = [book for book in watchlist.get('books', []) if str(book.get('olid')) != str(book_data['olid'])]
        elif category == 'movies-tv':
            response = get_movietv_info(item_id)
            movie_data = response.json()
            if movie_data.get("Response") == "True":
                if movie_data['Type'] == 'movie':
                    watchlist['movies'] = [m for m in watchlist.get('movies', []) if str(m.get('imdbID')) != str(movie_data['imdbID'])]
                elif movie_data['Type'] == 'series':
                    watchlist['tv'] = [t for t in watchlist.get('tv', []) if str(t.get('imdbID')) != str(movie_data['imdbID'])]
        elif category == 'games':
            item_data = get_bgg_game_info(item_id)
            if item_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany']:
                watchlist['video_games'] = [game for game in watchlist.get('video_games', []) if str(game.get('gameID')) != str(item_id)]
            else: 
                watchlist['games'] = [game for game in watchlist.get('games', []) if str(game.get('gameID')) != str(item_id)]

        # Save the updated watchlist
        profile.watchlist_past = watchlist
        profile.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def add_to_consumed_media(request, category, item_id):
    profile = request.user.profile
    watchlist_past = profile.watchlist_past # this is the original one
    # watchlist_past = PastWatchlist.objects.filter(user=request.user)
    
    if request.method == "POST":
        if not watchlist_past or not isinstance(watchlist_past, dict):
            watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games": []}
        else:
            watchlist = watchlist_past
        if category == 'movies-tv':
            movie_data = get_movietv_data_using_imdbID(item_id)
            if movie_data['Type'] == 'movie':
                if movie_data not in watchlist["movies"]:
                    watchlist["movies"].append(movie_data)
            if movie_data['Type'] == 'series':
                if movie_data not in watchlist["tv"]:
                    watchlist["tv"].append(movie_data)
        elif category == "books":
            response = get_book_info(item_id)
            book_data = response
            if "books" not in watchlist:
                watchlist["books"] = []
            if book_data not in watchlist["books"]:
                watchlist["books"].append(book_data)
        elif category == 'games': 
            game_data = get_bgg_game_info(item_id)
            if game_data['type'] in ['boardgame', 'boardgameperson', 'boardgamecompany']:
                watchlist["games"].append(game_data)
            elif game_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany', 'rpgitem']:
                watchlist["video_games"].append(game_data)
                print(watchlist['video_games'])

        profile.watchlist_past = watchlist
        profile.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_to_future_watchlist(request, category, item_id):
    if request.method == "POST":
        if category == 'movies-tv':
            movie_data = get_movietv_data_using_imdbID(item_id)
            movietv_category = 'movie' if movie_data['Type'] in ['movie'] else 'tv'
            category_ = get_media_category(category, item_id)
            FutureWatchlist.objects.get_or_create(
                    user=request.user,
                    category=category_,
                    item_id=item_id
            )

        elif category == 'books':
            book_data = get_book_info(item_id)
            FutureWatchlist.objects.get_or_create(
                user=request.user,
                category='book',
                item_id=item_id
            )

        elif category == 'games':
            games_data = get_bgg_game_info(item_id)
            game_category = 'videogame' if games_data['type'] in ['videogame', 'rpg'] else 'boardgame'
            FutureWatchlist.objects.get_or_create(
                user=request.user,
                category=game_category,
                item_id=item_id
            )

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def remove_from_future_watchlist(request, category, item_id):
    if request.method == "POST":
        if category == 'movies-tv':
            movie_data = get_movietv_data_using_imdbID(item_id)
            if movie_data['Type'] == 'movie':
                delete_future_watchlist_item(request, movie_data['imdbID'],'movie')
            if movie_data['Type'] == 'series':
                delete_future_watchlist_item(request, movie_data['imdbID'],'tv')
        if category == "books":
            book_data = get_book_info(item_id)
            delete_future_watchlist_item(request, item_id,'book')
        if category == 'games':
            games_data = get_bgg_game_info(item_id)
            if games_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany']:
                delete_future_watchlist_item(request, item_id,'videogame')
            else:
                delete_future_watchlist_item(request, item_id,'boardgame')

    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def add_to_favorites(request, category, item_id):
    if request.method == 'POST':
        if category == 'movies-tv':
            movie_data = get_movietv_data_using_imdbID(item_id)
            movietv_id = str(movie_data.get('imdbID', ''))
            category_type = 'movie' if movie_data.get('Type') == 'movie' else 'tv'
            Favorite.objects.get_or_create(
                user=request.user,
                category=category_type,
                item_id=item_id
            )

        elif category == 'books':
            book_data = get_book_info(item_id)
            Favorite.objects.get_or_create(
                user=request.user,
                category='book',
                item_id=item_id
            )

        elif category == 'games':
            games_data = get_bgg_game_info(item_id)
            game_category = 'videogame' if games_data['type'] in ['videogame', 'rpg'] else 'boardgame'
            Favorite.objects.get_or_create(
                user=request.user,
                category=game_category,
                item_id=item_id
            )
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def remove_from_favorites(request, category, item_id):
    if request.method == 'POST':
        if category == 'movies-tv':
            movie_data = get_movietv_data_using_imdbID(item_id)
            if movie_data['Type'] == 'movie':
                delete_favorite_item(request, movie_data['imdbID'],'movie')
            if movie_data['Type'] == 'series':
                delete_favorite_item(request, movie_data['imdbID'],'tv')
        if category == "books":
            book_data = get_book_info(item_id)
            delete_favorite_item(request, item_id,'book')
        if category == 'games':
            games_data = get_bgg_game_info(item_id)
            if games_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany']:
                delete_favorite_item(request, item_id,'videogame')
            else:
                delete_favorite_item(request, item_id,'boardgame')
    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
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
                        "description": media_data.get("description", ""), "image_url": media_data.get("image", "")}
            )

        except ValidationError as e:
            messages.error(request, str(e))  # Store error message in session

        return redirect(request.META.get("HTTP_REFERER", "/"))  # Redirect to the same page

    return redirect("/")  # Fallback in case of non-POST request
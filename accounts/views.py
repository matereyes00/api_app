from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash  # Keeps user logged in
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from.forms import CustomUserCreationForm, ProfileUpdateForm
from.models import Profile, Favorite, FutureWatchlist
from django.shortcuts import redirect
from django.contrib import messages

from .templates.API_.get import get_bgg_game_info, get_bgg_game_type,get_movietv_info,get_book_info, get_movietv_data
from .templates.API_.delete import delete_future_watchlist_item

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
    profile = request.user.profile  
    # Ensure watchlist is always a dictionary
    if not profile.watchlist_past or not isinstance(profile.watchlist_past, dict):
        profile.watchlist_past = {"movies": [], "games": [], "books": [], "tv": [], "video_games": []}
    # Convert string JSON to dict if necessary
    if isinstance(profile.watchlist_past, str):
        profile.watchlist_past = json.loads(profile.watchlist_past)
    watchlist = profile.watchlist_past
    # Get selected item to display details
    category = request.GET.get("category")  # Example: 'books', 'games', etc.
    item_id = request.GET.get("item_id")  # ID for API request
    item_data = None  # Default no data

    # Fetch API data if a category and item_id are selected
    if category and item_id:
        if category == "books":
            url = f"https://openlibrary.org/works/{item_id}.json"
            try:
                response = requests.get(url)
                response.raise_for_status()
                item_data = response.json()
                cover_url = None
                if item_data.get("covers"):
                    cover_id = item_data["covers"][0]
                    cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                item_data["cover_url"] = cover_url
            except requests.exceptions.RequestException as e:
                print(f"Error fetching book: {e}")

        elif category == "games":
            item_data = get_bgg_game_info(item_id) 
        
        elif category == "movies":
            api_key = os.getenv("OMDB_API_KEY")
            url = f"http://www.omdbapi.com/?t={item_id}&apikey={api_key}"
            try:
                response = requests.get(url)
                item_data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching movie/TV: {e}")

    # Handles logic for switching between views in the profile 
    selected_content = request.GET.get("lists", "view_favorites")
    selected_display_watchlist_item = request.GET.get("display_watchlist_item", "movie")

    return render(request, "profile/profile.html", {
        "profile": profile,
        "watchlist": watchlist,
        "selected_content": selected_content,
        "selected_display_watchlist_item": selected_display_watchlist_item,
        "category": category,
        "item_data": item_data,
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

        return redirect('accounts:profile')  # Redirect after form submission

    else:
        profile_form = ProfileUpdateForm(instance=profile)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'profile/editProfile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
def remove_from_consumed_media(request, category, item_id):
    profile = request.user.profile
    watchlist = profile.watchlist_past 
    if request.method == 'POST':
        if not watchlist or not isinstance(watchlist, dict):
            watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games": []}
        
        if category == 'book':
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
        elif category == 'game':
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
    watchlist_past = profile.watchlist_past
    if request.method == "POST":
        if not watchlist_past or not isinstance(watchlist_past, dict):
            watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games": []}
        else:
            watchlist = watchlist_past
        api_key = os.getenv('OMDB_API_KEY')
        if category == 'movies-tv':
            itemid = item_id
            title = item_id.replace("-", " ")  # Convert slug back to title
            api_url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
            response = requests.get(api_url)
            movie_data = response.json()
            
            movie_info = {
                "title": movie_data["Title"],
                "format": movie_data['Type'],
                "year": movie_data["Year"],
                "poster": movie_data["Poster"],
                "director": movie_data["Director"],
                "imdbID": movie_data['imdbID'],
                "format" : movie_data['Type']
            }
            if movie_info['format'] == 'movie':
                if movie_info not in watchlist["movies"]:
                    watchlist["movies"].append(movie_info)
            if movie_info['format'] == 'series':
                if movie_info not in watchlist["tv"]:
                    watchlist["tv"].append(movie_info)
        elif category == "book":
            response = get_book_info(item_id)
            book_data = response
            if "books" not in watchlist:
                watchlist["books"] = []
            if book_data not in watchlist["books"]:
                watchlist["books"].append(book_data)
        elif category == 'game': 
            game_data = get_bgg_game_info(item_id)
            if game_data['type'] in ['boardgame', 'boardgameperson', 'boardgamecompany']:
                watchlist["games"].append(game_data)
            elif game_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany']:
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
            itemid = item_id
            title = item_id.replace("-", " ")  # Convert slug back to title
            api_url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
            response = requests.get(api_url)
            movie_data = response.json()
            movietv_id = str(movie_data.get('imdbID', ''))
            if movie_data['Type'] == 'movie':
                FutureWatchlist.objects.get_or_create(
                user=request.user, category='movie', item_id=movietv_id
            )
            if movie_data['Type'] == 'series':
                FutureWatchlist.objects.get_or_create(
                user=request.user, category='tv', item_id=movietv_id
            )
        if category == 'book':
            book_data = get_book_info(item_id)
            FutureWatchlist.objects.get_or_create(
                user=request.user, category='book', item_id=item_id
            )
        if category == 'games':
            games_data = get_bgg_game_info(item_id)
            if games_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany']:
                FutureWatchlist.objects.get_or_create(user=request.user, category='videogame', item_id=item_id)
            else:
                FutureWatchlist.objects.get_or_create(user=request.user, category='boardgame', item_id=item_id)
        else:
            print("Not a valid item")

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def remove_from_future_watchlist(request, category, item_id):
    if request.method == "POST":
        print(f"CATEGORY: {category}")
        if category == 'movies-tv':
            movie_data = get_movietv_data(item_id)
            if movie_data['Type'] == 'movie':
                delete_future_watchlist_item(request, movie_data['imdbID'],'movie')
            if movie_data['Type'] == 'series':
                delete_future_watchlist_item(request, movie_data['imdbID'],'tv')
        if category == "book":
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
def add_movietvto_favorites(request, category, item_id):
    profile = request.user.profile
    api_url = f"https://www.omdbapi.com/?i={item_id}&apikey={api_key}"
    response = requests.get(api_url)
    data = response.json()

    if response.status_code == 200 and data.get("Title"):
        title = data["Title"]
        if not Favorite.objects.filter(user=request.user, category=category, item_id=item_id).exists():
            Favorite.objects.create(user=request.user, category=category, item_id=item_id, title=title)

    return redirect("accounts:profile")
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
    print(f"category:{category} || item_id:{item_id}")

    # Fetch API data if a category and item_id are selected
    if category and item_id:
        if category == "books":
            url = f"https://openlibrary.org/works/{item_id}.json"
            try:
                response = requests.get(url)
                response.raise_for_status()
                item_data = response.json()
                # Get book cover if available
                cover_url = None
                if item_data.get("covers"):
                    cover_id = item_data["covers"][0]
                    cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                item_data["cover_url"] = cover_url
            except requests.exceptions.RequestException as e:
                print(f"Error fetching book: {e}")

        elif category == "games":
            item_data = get_bgg_game_info(item_id)  # Assuming this function is already defined

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
        "item_data": item_data,  # Pass the fetched API data to the template
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
    watchlist = profile.watchlist_past  # Get current watchlist
    # Ensure watchlist structure
    if not watchlist or not isinstance(watchlist, dict):
        watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games": []}
    api_key = os.getenv('OMDB_API_KEY')  # Ensure API key is loaded
    print(f"Category: {category}")
    
    if category == 'books':
        watchlist['books'] = [book for book in watchlist.get('books', []) if str(book.get('olid')) != str(item_id)]
    elif category == 'movies-tv':
        response = get_movietv_info(item_id)
        movie_data = response.json()
        print(f"movies metadata: {movie_data}")
        if movie_data.get("Response") == "True":
            if movie_data['Type'] == 'movie':
                watchlist['movies'] = [m for m in watchlist.get('movies', []) if str(m.get('imdbID')) != str(movie_data['imdbID'])]
            elif movie_data['Type'] == 'series':
                watchlist['tv'] = [t for t in watchlist.get('tv', []) if str(t.get('imdbID')) != str(movie_data['imdbID'])]
    elif category == 'game':
        item_data = get_bgg_game_info(item_id)
        if item_data['type'] == 'videogame':
            watchlist['video_games'] = [game for game in watchlist.get('video_games', []) if str(game.get('gameID')) != str(item_id)]
        else: 
            watchlist['games'] = [game for game in watchlist.get('games', []) if str(game.get('gameID')) != str(item_id)]

    # Save the updated watchlist
    profile.watchlist_past = watchlist
    profile.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))



@login_required
def add_to_consumed_media(request, item_type, item_id):
    profile = request.user.profile
    watchlist_past = profile.watchlist_past
    if request.method == "POST":
        if not watchlist_past or not isinstance(watchlist_past, dict):
            watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games": []}
        else:
            watchlist = watchlist_past

        api_key = os.getenv('OMDB_API_KEY')
        print(f"This is the item_type: {item_type}")

        if item_type == 'movies-tv':
            itemid = item_id
            title = item_id.replace("-", " ")  # Convert slug back to title
            # print(f"=={title}")
            api_url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
            response = requests.get(api_url)
            movie_data = response.json()
            
            # if  movie_data.get("Response") == "True":
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
                print(movie_info['format'])
                if movie_info not in watchlist["tv"]:
                    watchlist["tv"].append(movie_info)

            # print(watchlist['movies'])
            # print(watchlist['tv'])
        elif item_type == "book":
            if "books" not in watchlist:
                watchlist["books"] = []
            book_info = {"olid": item_id}
            if book_info not in watchlist["books"]:
                watchlist["books"].append(book_info)
        elif item_type in ["game", "video_game"]:
            if item_type == "game":
                watchlist["games"].append({"gameID": item_id})
            elif item_type == "video_game":
                watchlist["video_games"].append({"gameID": item_id})

        # Save the updated watchlist
        profile.watchlist_past = watchlist
        profile.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect(request.META.get('HTTP_REFERER', '/'))



@login_required
def add_to_future_watchlist(request, category, item_id):
    profile = request.user.profile
    future_watchlist = FutureWatchlist.objects.filter(user=request.user)

    future_watchlist.item_id = item_id
    future_watchlist.category = category
    future_watchlist.save()

@login_required
def add_movietvto_favorites(request, category, item_id):
    profile = request.user.profile
    # Fetch movie/TV show details from OMDb API
    api_url = f"https://www.omdbapi.com/?i={item_id}&apikey={api_key}"
    response = requests.get(api_url)
    data = response.json()

    # Ensure API call was successful and title exists
    if response.status_code == 200 and data.get("Title"):
        title = data["Title"]
        # Check if it already exists in the favorites list
        if not Favorite.objects.filter(user=request.user, category=category, item_id=item_id).exists():
            Favorite.objects.create(user=request.user, category=category, item_id=item_id, title=title)

    return redirect("accounts:profile")



# RETRIEVING API INFO
def get_bgg_game_info(game_id):
    url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={game_id}&stats=1"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        root = ET.fromstring(response.content)
        game_data = {}
        game_data = {"gameID": game_id}  # Store game_id here

        # More robust way to extract data, handling missing elements:
        name_element = root.find('.//name[@type="primary"]')  # Get the primary name
        game_data['name'] = name_element.get('value') if name_element is not None else "No Name"
        year_element = root.find('.//yearpublished')
        game_data['yearpublished'] = year_element.get('value') if year_element is not None else "No Year"
        description_element = root.find('.//description')
        game_data['description'] = description_element.text if description_element is not None else "No Description"
        minplayers_element = root.find('.//minplayers')
        game_data['minplayers'] = minplayers_element.get('value') if minplayers_element is not None else "No Min Players"
        maxplayers_element = root.find('.//maxplayers')
        game_data['maxplayers'] = maxplayers_element.get('value') if maxplayers_element is not None else "No Max Players"
        playingtime_element = root.find('.//playingtime')
        game_data['playingtime'] = playingtime_element.get('value') if playingtime_element is not None else "No Playing Time"
        average_element = root.find('.//average')
        game_data['ratingaverage'] = average_element.get('value') if average_element is not None else "No Rating"
        image_element = root.find('.//image')
        game_data['image'] = image_element.text if image_element is not None else None

        game_type = get_bgg_game_type(game_data['name'])
        game_data['type'] = game_type

        return game_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error: {e}")
        return None

def get_bgg_game_type(game_name):
    """Fetches the game type (boardgame, RPG, videogame, etc.) from the BoardGameGeek search API."""
    search_url = f"https://www.boardgamegeek.com/xmlapi2/search?query={game_name}&exact=1"
    try:
        response = requests.get(search_url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        item = root.find('.//item')

        if item is not None:
            return item.get('type')  # Example: "boardgame", "rpgitem", "videogame"
        return "Unknown"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching game type: {e}")
        return "Unknown"
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return "Unknown"

def get_movietv_info(movietv_title):
    api_key = os.getenv('OMDB_API_KEY')
    url = f'http://www.omdbapi.com/?t={movietv_title}&apikey={api_key}'
    response = requests.get(url)
    return response

def get_book_info(book_olid):
    url = f"https://openlibrary.org/works/{book_olid}.json"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"title": "Unknown", "author": "Unknown", "cover_url": None}

    book_data = response.json()
    cover_url = None

    if book_data.get("covers"):
        cover_id = book_data["covers"][0]
        cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-M.jpg"

    # Fetch author name
    author_name = "Unknown"
    if "authors" in book_data and book_data["authors"]:
        author_key = book_data["authors"][0].get("author", {}).get("key")  # Get author key
        if author_key:
            author_url = f"https://openlibrary.org{author_key}.json"
            author_response = requests.get(author_url)
            if author_response.status_code == 200:
                author_data = author_response.json()
                author_name = author_data.get("name", "Unknown")

    return {
        "title": book_data.get("title", "Unknown"),
        "author": author_name,
        "cover_url": cover_url,
        "olid": book_olid,
    }
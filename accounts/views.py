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
from.models import Profile, Favorite

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
        profile.watchlist_past = {"movies": [], "games": [], "books": [], "tv":[], "video_games":[]}
    
    # Convert string JSON to dict if necessary
    if isinstance(profile.watchlist_past, str):
        profile.watchlist_past = json.loads(profile.watchlist_past)

    watchlist = profile.watchlist_past

    # handles logic for switching between views in the profile 
    # watchlist view (seen/unseen) , favorites view 
    selected_content = request.GET.get("lists", "view_favorites")  
    # dislpay the given media
    selected_display_watchlist_item = request.GET.get("display_watchlist_item", "movie") 

    return render(request, "profile/profile.html", 
    {
        "profile": profile, 
        "selected_content": selected_content,
        "selected_display_watchlist_item": selected_display_watchlist_item,
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
def remove_from_watchlist(request, category, item_id):
    profile = request.user.profile
    watchlist = profile.watchlist_past  # Get current watchlist
    if category == 'book':
        watchlist['books'] = [book for book in watchlist.get('books', []) if book['olid'] != item_id]
    elif category == 'tv':
        title = item_id.replace("-", " ")  # Convert slug back to title
        api_url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(api_url)
        tv_data = response.json()
        if 'imdbID' in tv_data:
            tv_id = tv_data["imdbID"]
            print(watchlist['tv'])
            watchlist['tv'] = [t for t in watchlist.get('tv', []) if t.get('imdbID') != tv_id]
    elif category == 'movie':
        title = item_id.replace("-", " ")  # Convert slug back to title
        api_url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(api_url)
        movie_data = response.json()
        movie_id = movie_data["imdbID"]
        if movie_id:
            watchlist['movies'] = [movie for movie in watchlist.get('movies', []) if movie['imdbID'] != movie_id]
    elif category == 'game':
        watchlist['games'] = [game for game in watchlist.get('games', []) if game['gameID'] != item_id]
    elif category == 'video_game':
        watchlist['video_games'] = [game for game in watchlist.get('video_games', []) if game['gameID'] != item_id]
    # Save updated watchlist
    profile.watchlist_past = watchlist
    profile.save()

    return redirect('accounts:profile')  # Success


@login_required
def add_to_watchlist(request, item_type, item_id):
    profile = request.user.profile  # Get user's profile

    # Retrieve or initialize the watchlist
    if not profile.watchlist_past or not isinstance(profile.watchlist_past, dict):
        watchlist = {"movies": [], "tv": [], "games": [], "books": [], "video_games":[]}  # Default structure
    else:
        watchlist = profile.watchlist_past  # Retrieve existing watchlist

    # Ensure the key exists
    if "movies" not in watchlist:
        watchlist["movies"] = []
    if "tv" not in watchlist:
        watchlist["tv"] = []
    if "games" not in watchlist:
        watchlist["games"] = []
    if "books" not in watchlist:
        watchlist["books"] = []
    if "video_games" not in watchlist:
        watchlist["video_games"] = []
    # Fetch full movie details from the API
    if item_type == "movie" or item_type == 'tv':
        title = item_id.replace("-", " ")  # Convert slug back to title
        api_url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
        response = requests.get(api_url)
        movie_data = response.json()
        
        if item_type == "movie" and movie_data.get("Response") == "True":
            movie_info = {
                "title": movie_data["Title"],
                "format": movie_data['Type'],
                "year": movie_data["Year"],
                "poster": movie_data["Poster"],
                "director": movie_data["Director"],
                "imdbID": movie_data["imdbID"],
            }
        if movie_info['format'] == 'movie':
            if movie_info not in watchlist["movies"]:
                watchlist["movies"].append(movie_info)
        if movie_info['format'] == 'series':
            if movie_info not in watchlist["movies"]:
                watchlist["tv"].append(movie_info)

    # Handle adding games
    if item_type == "game" or "video_game":
        game_id = item_id  # Since item_id is already game_id from the URL
        game_data = get_bgg_game_info(game_id)  # Fetch game data
        if game_data["name"] != "No Name":  # Ensure valid data was retrieved
            game_info = {
                "title": game_data["name"],
                "year": game_data["yearpublished"],
                "type": game_data["type"],
                "poster": game_data["image"],
                "gameID": game_id,
            }

            print(game_info)

            if game_info['type'] == 'videogame' or game_info['type'] == 'rpgitem':
                watchlist["video_games"].append(game_info)
            elif game_info['type'] == 'boardgame':
                watchlist["games"].append(game_info)
    if item_type == "book":
        book_olid = item_id  # This is the OLID from the URL
        book_data = get_book_info(book_olid)
        
        book_info = {
            "title": book_data.get("title", "Unknown"),
            "author": book_data.get("author", "Unknown"),
            "cover_url": book_data.get("cover_url"),
            "olid": book_olid,
        }

        if book_info not in watchlist["books"]:  # Avoid duplicates
            watchlist["books"].append(book_info)

    # Save updated watchlist
    profile.watchlist = watchlist
    profile.save()

    return redirect("accounts:profile")  # Redirect to the profile page


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
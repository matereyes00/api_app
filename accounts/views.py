from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from.forms import CustomUserCreationForm
from.models import Profile

import json
import requests
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env

class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # Use the custom form
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"
    
@login_required
def profile_view(request):
    profile = request.user.profile  

    # Ensure watchlist is always a dictionary
    if not profile.watchlist or not isinstance(profile.watchlist, dict):
        profile.watchlist = {"movies": [], "games": [], "books": []}
    
    # Convert string JSON to dict if necessary
    if isinstance(profile.watchlist, str):
        profile.watchlist = json.loads(profile.watchlist)

    watchlist = profile.watchlist

    return render(request, "profile/profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return render(request, 'profile/profile.html', {'profile': profile})
    else:
        form = CustomUserCreationForm(instance=profile)  # Pass the instance here
    return render(request, 'profile/editProfile.html', {'form': form})

@login_required
def add_to_watchlist(request, item_type, item_id):
    profile = request.user.profile  # Get user's profile
    api_key = os.getenv('OMDB_API_KEY')

    # Retrieve or initialize the watchlist
    if not profile.watchlist or not isinstance(profile.watchlist, dict):
        watchlist = {"movies": [], "games": [], "books": []}  # Default structure
    else:
        watchlist = profile.watchlist  # Retrieve existing watchlist

    # Ensure the key exists
    if "movies" not in watchlist:
        watchlist["movies"] = []
    if "games" not in watchlist:
        watchlist["games"] = []
    if "books" not in watchlist:
        watchlist["books"] = []

    # Fetch full movie details from the API
    if item_type == "movie" :
        movie_title = item_id.replace("-", " ")  # Convert slug back to title
        api_url = f"https://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
        response = requests.get(api_url)
        movie_data = response.json()
        
        if item_type == "movie" and movie_data.get("Response") == "True":
            movie_info = {
                "title": movie_data["Title"],
                "year": movie_data["Year"],
                "poster": movie_data["Poster"],
                "director": movie_data["Director"],
                "imdbID": movie_data["imdbID"],
            }
        if movie_info not in watchlist["movies"]:
            watchlist["movies"].append(movie_info)

    # Handle adding games
    if item_type == "game":
        game_id = item_id  # Since item_id is already game_id from the URL
        game_data = get_bgg_game_info(game_id)  # Fetch game data
        print(game_data)
        if game_data["name"] != "No Name":  # Ensure valid data was retrieved
            game_info = {
                "title": game_data["name"],
                "year": game_data["yearpublished"],
                "poster": game_data["image"],
                "gameID": game_id,
            }
            # Avoid duplicates
            if game_info not in watchlist["games"]:
                watchlist["games"].append(game_info)
                print(f"Added game to watchlist: {game_info}")

    if item_type == "book":
        book_olid = item_id  # This is the OLID from the URL
        print(book_olid)
        book_data = get_book_info(book_olid)
        print(book_data)
        
        book_info = {
            "title": book_data.get("title", "Unknown"),
            "author": book_data.get("author", "Unknown"),
            "cover_url": book_data.get("cover_url"),
            "olid": book_olid,
        }

        if book_info not in watchlist["books"]:  # Avoid duplicates
            watchlist["books"].append(book_info)

    profile.watchlist = watchlist
    profile.save()

    return redirect("accounts:profile")


    # Save updated watchlist
    profile.watchlist = watchlist
    profile.save()

    return redirect("accounts:profile")  # Redirect to the profile page


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

        return game_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error: {e}")
        return None


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
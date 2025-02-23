import os
import json  
import requests
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from urllib.parse import quote  # Import for URL encoding
from django.shortcuts import render
from django.core.cache import cache
from .forms import RegisterForm, LoginForm

from django.urls import reverse

load_dotenv()  # Load environment variables from.env

def index(request):
    return render(request, 'main/index.html')

def profile_view_extend(request):
    return redirect(reverse('accounts:profile'))

@login_required(login_url='accounts/login/')
def search(request, category):
    if request.method == 'POST':
        query = request.POST.get('query')  # Use the same input name for all searches

        if category == 'Movies and TV':
            api_key = os.getenv('OMDB_API_KEY')
            url = f'http://www.omdbapi.com/?s={query}&apikey={api_key}'
            response = requests.get(url)
            data = response.json()
            results = data.get('Search', [])
            error_message = data.get('Error', None)
            template = 'main/movie_search_results.html'

        elif category == 'games':
            url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame,boardgameexpansion,videogame"
            response = requests.get(url)
            root = ET.fromstring(response.content)
            results = []
            for item in root.findall('item'):
                game_id = item.get('id')
                name_element = item.find('name')
                name = name_element.get('value') if name_element is not None else "No Name"
                
                year_element = item.find('yearpublished')
                yearpublished = year_element.get('value') if year_element is not None else "No Year"

                results.append({
                    'id': game_id,
                    'name': name,
                    'yearpublished': yearpublished
                })
            
            template = 'main/game_search_results.html'

        elif category == 'books':
            url = f"https://openlibrary.org/search.json?q={query}"
            response = requests.get(url)
            data = response.json()
            books = data.get('docs', [])
            results = [
                {
                    'title': book.get('title'),
                    'author_name': book.get('author_name'),
                    'olid': book.get('key').split('/')[-1] if book.get('key') else None,
                    'isbn': book.get('isbn')
                }
                for book in books
            ]
            template = 'main/book_search_results.html'

        else:
            return render(request, 'main/base_search.html', {'error_message': 'Invalid category'})

        return render(request, template, {'results': results, 'query': query, 'error_message': error_message if 'error_message' in locals() else None})
    
    return render(request, 'main/base_search.html', {'category': category})

@login_required(login_url='accounts/login/')
def movie_tv_detail(request, Title):
    api_key = os.getenv('OMDB_API_KEY')
    url = f'http://www.omdbapi.com/?t={Title}&apikey={api_key}'  # Use 't' for title lookup
    response = requests.get(url)
    movie_data = response.json()
    return render(request, 'main/movie_details.html', {'movie': movie_data})


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

@login_required(login_url='accounts/login/')   
def game_detail(request, game_id):
    game_data = get_bgg_game_info(game_id)
    print(game_data)
    query = request.GET.get('q')
    if game_data:
        return render(request, 'main/game_detail.html', {'game': game_data, 'query': query})
    else:
        return render(request, 'main/game_search.html', {'error_message': 'Game not found.'})


@login_required(login_url='accounts/login/')
def book_detail(request, olid):  # Changed parameter to 'olid'
    url = f"https://openlibrary.org/works/{olid}.json"  # Use works endpoint

    try:
        response = requests.get(url)
        response.raise_for_status()
        book_data = response.json()

        cover_url = None  # Initialize cover_url

        if book_data.get('covers'): # Check if the covers key exists
            cover_id = book_data['covers'][0]
            cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-M.jpg" # Use 'id' as the key

        elif olid: # If no covers key exists, try to construct the url with the olid
            cover_url = f"http://covers.openlibrary.org/b/olid/{olid}-M.jpg"  # Use 'olid' as the key

        book_data['cover_url'] = cover_url  # Set the cover_url in book_data

        return render(request, 'main/book_details.html', {
            'book': book_data, 
            'book_olid':olid})

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return render(request, 'main/search.html', {'error_message': 'Error fetching book details.'})
    except json.JSONDecodeError as e:  # Catch potential JSON errors
        print(f"Error processing JSON: {e}")
        return render(request, 'main/search.html', {'error_message': 'Error processing book data.'})

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


load_dotenv()  # Load environment variables from.env

def index(request):
    return render(request, 'main/index.html')

@login_required(login_url='accounts/login/')
def profile_view(request):
    profile = request.user.profile  # Access the user's profile
    return render(request, 'main/profile.html', {'profile': profile})

@login_required(login_url='accounts/login/')
def search_movies_tv(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        api_key = os.getenv('OMDB_API_KEY')
        url = f'http://www.omdbapi.com/?s={title}&apikey={api_key}'  # Use 's' for search
        response = requests.get(url)
        movie_data = response.json()
        if movie_data.get('Search'):  # Check if 'Search' key exists (important!)
            movies = movie_data['Search']  # Access the list of movies
            return render(request, 'main/movie_search_results.html', {'movie': movies, 'title': title})  # Pass the list
        elif movie_data.get('Error'): # Check if the api returned an error.
            error_message = movie_data['Error']
            return render(request, 'main/movie_tv_search.html', {'error_message': error_message}) # If it did, return the error message.
        else:
            return render(request, 'main/movie_search_results.html', {'movie': None, 'title': title}) # Handle no results case
    else:
        return render(request, 'main/movie_tv_search.html')

@login_required(login_url='accounts/login/')
def movie_tv_detail(request, Title):
    api_key = os.getenv('OMDB_API_KEY')
    url = f'http://www.omdbapi.com/?t={Title}&apikey={api_key}'  # Use 't' for title lookup
    response = requests.get(url)
    movie_data = response.json()
    return render(request, 'main/movie_details.html', {'movie': movie_data})
    
@login_required(login_url='accounts/login/')
def search_games(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame,boardgameexpansion,videogame"
        try:
            response = requests.get(url)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            results = []
            for item in items:
                game_id = item.get('id')
                name = item.find('name').get('value') if item.find('name') is not None else "No Name"
                yearpublished = item.find('yearpublished').get('value') if item.find('yearpublished') is not None else "No Year"
                results.append({
                    'id': game_id,
                    'name': name,
                    'yearpublished': yearpublished
                })
            return render(request, 'main/game_search_results.html', {'games': results, 'query': query})

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return render(request, 'main/game_search.html', {'error_message': 'Error searching games.'})
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return render(request, 'main/game_search.html', {'error_message': 'Error parsing BGG response.'})

    else:
        return render(request, 'main/game_search.html')

def get_bgg_game_info(game_id):
    url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={game_id}&stats=1"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        root = ET.fromstring(response.content)
        game_data = {}

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

@login_required(login_url='accounts/login/')   
def game_detail(request, game_id):
    game_data = get_bgg_game_info(game_id)
    query = request.GET.get('q')
    if game_data:
        return render(request, 'main/game_detail.html', {'game': game_data, 'query': query})
    else:
        return render(request, 'main/game_search.html', {'error_message': 'Game not found.'})


@login_required(login_url='accounts/login/')
def search_books(request):
    if request.method == 'POST':
        query = request.POST.get('title')
        # encoded_query = quote(query)  # URL encode the query
        url = f"https://openlibrary.org/search.json?q={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP errors
            book_data = response.json()
            books = book_data.get('docs', [])  # Extract the book list

            books_for_template = []
            for book in books:
                olid = None
                if book.get('key'): # Check if OLID exists
                    olid = book['key'].split('/')[-1] # Extract OLID from the key
                books_for_template.append({
                    'title': book.get('title'),
                    'author_name': book.get('author_name'),
                    'olid': olid, # Add OLID
                    'isbn': book.get('isbn') # Keep ISBN if available
                })

            if books_for_template: # Check if the list is not empty
                return render(request, 'main/book_search_results.html', {'books': books_for_template, 'query': query})
            else:
                return render(request, 'main/search.html', {'error_message': 'No books found for that search.'}) # Display a no results message

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return render(request, 'main/search.html', {'error_message': 'Error searching books.'})
        except (KeyError, TypeError) as e:
            print(f"Error processing JSON: {e}")
            return render(request, 'main/search.html', {'error_message': 'Error processing book data.'})

    else:
        return render(request, 'main/search.html')


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

        return render(request, 'main/book_details.html', {'book': book_data})

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return render(request, 'main/search.html', {'error_message': 'Error fetching book details.'})
    except json.JSONDecodeError as e:  # Catch potential JSON errors
        print(f"Error processing JSON: {e}")
        return render(request, 'main/search.html', {'error_message': 'Error processing book data.'})

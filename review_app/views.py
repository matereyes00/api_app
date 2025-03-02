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

from accounts.models import Profile, Favorite, FutureWatchlist
from .templates.API.get import get_bgg_game_info, get_bgg_game_type, get_movietv_info, get_book_info 
from .templates.API.get import search_api_book, search_api_movies_tv, get_movietv_data_using_imdbID
from .templates.API.get import search_api_games, is_movietv_in_consumed_media
from .templates.API.get import is_book_in_consumed_media,is_game_in_consumed_media

from django.urls import reverse

load_dotenv()  # Load environment variables from.env

def index(request):
    return render(request, 'main/index.html')

def profile_view_extend(request):
    return redirect(reverse('accounts:profile'))

@login_required(login_url='accounts/login/')
def search(request, category):
    if request.method == 'POST':
        query = request.POST.get('query')
        if category == 'movies-tv':
            response = search_api_movies_tv(query) 
            data = response.json()
            results = data.get('Search', [])
            error_message = data.get('Error', None)
        elif category == 'games':
            response = search_api_games(query)
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
        elif category == 'books':
            response = search_api_book(query)
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

        else:
            return render(request, 'main/baseSearch.html', {'error_message': 'Invalid category'})

        template = 'main/baseSearch.html'
        return render(request, template, {'category':category,'results': results, 'query': query, 'error_message': error_message if 'error_message' in locals() else None})
    
    return render(request, 'main/baseSearch.html', {'category': category})

@login_required(login_url='accounts/login/')
def item_details(request, category, item_id):
    context = {}
    user_profile = request.user.profile
    watchlist_past = user_profile.watchlist_past
    
    if isinstance(watchlist_past, str):
        watchlist_past = json.loads(watchlist_past) if watchlist_past else {}
    context['category'] = category
    item_id = str(item_id)
    if category == "books":
        url = f"https://openlibrary.org/works/{item_id}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            book_data = response.json()
            # Handle cover image
            cover_url = None
            if book_data.get('covers'):
                cover_id = book_data['covers'][0]
                cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            book_data['cover_url'] = cover_url
            book_data['olid'] = item_id  # Explicitly store the OLID
            context['book'] = book_data
            context['book_olid'] = item_id  # Set OLID in context
            book_attr_id = "olid"
            
            #Check if item is in a user's saved items
            consumed_media = user_profile.watchlist_past.get("books", [])
            context['book_in_consumed_media'] = is_book_in_consumed_media(consumed_media, book_attr_id, item_id)
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category='book', item_id=item_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
            print(f"{book_data['title']} is in futurewatchlist? : {item_in_future_watchlist}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return render(request, 'main/baseSearch.html', {'error_message': 'Error fetching book details.'})
        except json.JSONDecodeError as e:
            print(f"Error processing JSON: {e}")
            return render(request, 'main/baseSearch.html', {'error_message': 'Error processing book data.'})
    
    elif category == "games":
        game_data = get_bgg_game_info(item_id)
        context['game'] = game_data
        context['game_id'] = str(game_data['gameID'])
        games_attr_id = "gameID"
        if game_data['type'] in ['videogame', 'videogamecompany', 'rpg', 'rpgperson', 'rpgcompany']:
            consumed_media = user_profile.watchlist_past.get("video_games", [])
            context['consumed_media'] = consumed_media
            context['videogame_in_consumed_media'] = is_game_in_consumed_media(consumed_media, games_attr_id, item_id)
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category='videogame', item_id=item_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
        else:
            consumed_media = user_profile.watchlist_past.get("games", [])
            context['consumed_media'] = consumed_media
            context['boardgame_in_consumed_media'] = is_game_in_consumed_media(consumed_media, games_attr_id, item_id)
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category='boardgame', item_id=item_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
    
    elif category == "movies-tv":
        response = get_movietv_data_using_imdbID(item_id)
        movie_data = response.json()
        context['movie'] = movie_data
        movietv_id = str(movie_data.get('imdbID', ''))
        consumed_media = user_profile.watchlist_past.get('movies', [])
        consumed_media += user_profile.watchlist_past.get('tv', [])  
        context['consumed_media'] = consumed_media
        context['category'] = category
        if movie_data['Type'] == 'movie':
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category='movie', item_id=movietv_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
        else:
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category='tv', item_id=movietv_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
        
        context['movietv_in_consumed_media'] = is_movietv_in_consumed_media(consumed_media, "imdbID", movietv_id)
        
    return render(request, "main/baseItemDetails.html", context)
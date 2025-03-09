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

from api_app.accounts.models import Profile, FutureWatchlist, Favorite
from get import get_bgg_game_info, get_bgg_game_type, get_movietv_info, get_book_info, get_movietv_data_using_imdbID
from getExists import is_movietv_in_consumed_media, is_book_in_consumed_media,is_game_in_consumed_media
from getSearch import search_api_book, search_api_movies_tv, search_api_games, search_all_media

from django.urls import reverse

load_dotenv()  # Load environment variables from.env

def index(request):
    return render(request, 'main/index.html')

def profile_view_extend(request):
    return redirect(reverse('api_app.accounts:profile'))

@login_required(login_url='accounts/login/')
def search(request, category):
    if request.method == 'POST':
        query = request.POST.get('query')
        results = search_all_media(query, category)
        template = 'main/baseSearch.html'
        context = {'category':category,
                'results': results,
                'query': query, 
                'error_message': error_message if 'error_message' in locals() else None}
        return render(request, template, context)
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
    context['item_id'] = item_id
    
    if category == "books":
        try:
            book_data = get_book_info(item_id)
            book_data['olid'] = item_id  
            context['book'] = book_data
            context['book_olid'] = item_id  # Set OLID in context
            book_attr_id = "olid"
            cat ="book"
            
            #Check if item is in a user's saved items
            consumed_media = user_profile.watchlist_past.get("books", [])
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            item_in_favorites = Favorite.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            context['is_item_in_past_watchlist'] = is_book_in_consumed_media(consumed_media, book_attr_id, item_id)
            context['list_category'] = cat
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
            context["is_item_in_favorites"] = item_in_favorites

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
            cat = 'videogame'
            context['consumed_media'] = consumed_media
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            item_in_favorites = Favorite.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            context['list_category'] = cat
            context['is_item_in_past_watchlist'] = is_game_in_consumed_media(consumed_media, games_attr_id, item_id)
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
            context["is_item_in_favorites"] = item_in_favorites

        else:
            consumed_media = user_profile.watchlist_past.get("games", [])
            context['consumed_media'] = consumed_media
            cat = 'boardgame'
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            item_in_favorites = Favorite.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            context['list_category'] = cat
            context['is_item_in_past_watchlist'] = is_game_in_consumed_media(consumed_media, games_attr_id, item_id)
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
            context["is_item_in_favorites"] = item_in_favorites

    
    elif category == "movies-tv":
        movie_data = get_movietv_data_using_imdbID(item_id)
        # movie_data = response.json()
        context['movie'] = movie_data
        movietv_id = str(movie_data.get('imdbID', ''))
        consumed_media = user_profile.watchlist_past.get('movies', [])
        consumed_media += user_profile.watchlist_past.get('tv', [])  
        context['consumed_media'] = consumed_media
        context['category'] = category
        
        if movie_data['Type'] == 'movie':
            cat = movie_data['Type']
            context['list_category'] = cat
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=cat, item_id=movietv_id).exists()
            item_in_favorites = Favorite.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
            context["is_item_in_favorites"] = item_in_favorites
            context['is_item_in_past_watchlist'] = is_movietv_in_consumed_media(consumed_media, "imdbID", movietv_id)
            
        else:
            cat = 'tv'
            context['list_category'] = cat
            item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=cat, item_id=movietv_id).exists()
            item_in_favorites = Favorite.objects.filter(user=request.user, category=cat, item_id=item_id).exists()
            context["is_item_in_future_watchlist"] = item_in_future_watchlist
            context["is_item_in_favorites"] = item_in_favorites
            context['is_item_in_past_watchlist'] = is_movietv_in_consumed_media(consumed_media, "imdbID", movietv_id)
    return render(request, "main/baseItemDetails.html", context)
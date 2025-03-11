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

from api_app.accounts.models import Profile, FutureWatchlist, Favorite, PastWatchlist
from get import get_bgg_game_info, get_bgg_game_type, get_movietv_info, get_book_info, get_movietv_data_using_imdbID, fetch_media_info, get_media_category
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
    category_ = get_media_category(category, item_id) # movie, tv, book, videogame, boardgame
    data = fetch_media_info(category_, item_id)
    context['item_id'] = item_id
    context['category'] = category #movies-tv,books,games
    if category == 'books': context['book'] = data
    elif category == 'movies-tv': context['movie'] = data
    elif category == 'games': context['game'] = data

    item_in_past_Watchlist = PastWatchlist.objects.filter(user=request.user, category=category_, item_id=item_id).exists()
    item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=category_, item_id=item_id).exists()
    item_in_favorites = Favorite.objects.filter(user=request.user, category=category_, item_id=item_id).exists()
    context['list_category'] = category_
    context['is_item_in_past_watchlist'] = item_in_past_Watchlist
    context["is_item_in_future_watchlist"] = item_in_future_watchlist
    context["is_item_in_favorites"] = item_in_favorites
    
    return render(request, "main/baseItemDetails.html", context)
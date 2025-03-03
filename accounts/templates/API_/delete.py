import os
import json  
import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render, get_object_or_404
from accounts.models import Profile, Favorite, FutureWatchlist


def delete_future_watchlist_item(request, item_id, category):
    item_to_check = get_object_or_404(FutureWatchlist, user=request.user, category=category, item_id=item_id)
    item_in_future_watchlist = FutureWatchlist.objects.filter(user=request.user, category=category, item_id=item_id).exists()
    if item_in_future_watchlist == True:
        item_to_check.delete()
        
def delete_favorite_item(request, item_id, category):
    item_to_check = get_object_or_404(Favorite, user=request.user, category=category, item_id=item_id)
    item_in_favorites = Favorite.objects.filter(user=request.user, category=category, item_id=item_id).exists()
    if item_in_favorites == True:
        item_to_check.delete()
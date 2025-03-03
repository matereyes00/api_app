import os
import json  
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from.env

api_key = os.getenv('OMDB_API_KEY')
# create a search def for books, movies-tv, and games
def search_all_media(query, category):
    if category == 'movies-tv':
        response = search_api_movies_tv(query)
        data = response.json()
        results = data.get('Search', [])
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
    return results

def search_api_book(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    return response

def search_api_movies_tv(query):
    url = f'http://www.omdbapi.com/?s={query}&apikey={api_key}'
    response = requests.get(url)
    return response

def search_api_games(query):
    url = f"https://boardgamegeek.com/xmlapi2/search?query={query}&type=boardgame,boardgameexpansion,videogame"
    response = requests.get(url)
    return response
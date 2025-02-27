import os
import json  
import requests
import xml.etree.ElementTree as ET

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
    
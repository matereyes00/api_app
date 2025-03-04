import os
import json  
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from.env

api_key = os.getenv('OMDB_API_KEY')

def is_book_in_consumed_media(users_consumed_media, attr_id, id_):
    if isinstance(users_consumed_media, list):
        if all(isinstance(item, dict) for item in users_consumed_media):  
            book_in_consumed_media = any(str(item.get(attr_id)) == str(id_) for item in users_consumed_media)
        else:  
            book_in_consumed_media = id_ in users_consumed_media
    else:
        book_in_consumed_media = False  
    return book_in_consumed_media

def is_game_in_consumed_media(users_consumed_media, attr_id, id_):
    if isinstance(users_consumed_media, list):
        if all(isinstance(item, dict) for item in users_consumed_media):  
            game_in_consumed_media = any(str(item.get(attr_id)) == str(id_) for item in users_consumed_media)
        else:  
            game_in_consumed_media = id_ in users_consumed_media
    else:
        game_in_consumed_media = False  # Default to False if data format is unexpected
    return game_in_consumed_media

def is_movietv_in_consumed_media(users_consumed_media, attr_id, id_):
    if isinstance(users_consumed_media, list):
            if all(isinstance(item, dict) for item in users_consumed_media):  
                movietv_in_consumed_media = any(str(item.get(attr_id)) == id_ for item in users_consumed_media)
            else:  
                movietv_in_consumed_media = id_ in users_consumed_media
    else:
        movietv_in_consumed_media = False 
    return movietv_in_consumed_media

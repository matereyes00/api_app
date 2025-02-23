from django.urls import path
from . import views as v

app_name = 'review_app'  # Make sure this matches

urlpatterns=[
  path('',v.index, name='index'),
  # path('search_movie_or_show/',v.search_movies_tv, name='search_movies_tv'),
  path('search/<str:category>/', v.search, name='search'),  # General search view
  path('movie_detail/<str:Title>/',v.movie_tv_detail, name='movie_tv_detail'),
  # path('search_game/', v.search_games, name='search_games'),
  path('game_detail/<int:game_id>/', v.game_detail, name='game_detail'), 
  # path('search_books/', v.search_books, name='search_books'),
  path('book_detail/<str:olid>/', v.book_detail, name='book_detail'),  # Use OLID in URL
]
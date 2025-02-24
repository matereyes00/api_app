from django.urls import path
from . import views as v

app_name = 'review_app'  # Make sure this matches

urlpatterns=[
  path('',v.index, name='index'),
  path('search/<str:category>/', v.search, name='search'),  # General search view
  path("details/<str:category>/<str:item_id>/", v.item_details, name="item_details"),

  # path('movie_detail/<str:Title>/',v.movie_tv_detail, name='movie_tv_detail'),
  # path('game_detail/<int:game_id>/', v.game_detail, name='game_detail'), 
  # path('book_detail/<str:olid>/', v.book_detail, name='book_detail'),  # Use OLID in URL
]
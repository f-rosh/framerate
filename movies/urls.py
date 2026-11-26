from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_results_view, name='search'),
    path('api/search/', views.ajax_search_view, name='ajax_search'),
    path('movie/<int:tmdb_id>/', views.movie_detail_view, name='movie_detail'),
]
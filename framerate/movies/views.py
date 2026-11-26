from django.shortcuts import render
from django.http import JsonResponse
from .models import Movie
from .tmdb_service import (
    search_movies,
    get_movie_detail,
    get_trending_movies,
    TMDB_IMAGE_SMALL,
    TMDB_IMAGE_TRENDING,
)
from reviews.models import Review


def home_view(request):
    """Landing page: trending movies + recent community reviews."""
    trending = get_trending_movies(limit=12)
    recent_reviews = (
        Review.objects
        .select_related('user', 'movie')
        .order_by('-created_at')[:5]
    )
    return render(request, 'movies/home.html', {
        'trending': trending,
        'trending_image_base': TMDB_IMAGE_TRENDING,
        'recent_reviews': recent_reviews,
    })


def search_results_view(request):
    """Full search results page."""
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = search_movies(query)
    return render(request, 'movies/search_results.html', {
        'query': query,
        'results': results,
    })


def movie_detail_view(request, tmdb_id):
    """Movie detail page with TMDb data + community reviews."""
    movie_data = get_movie_detail(tmdb_id)
    if not movie_data:
        return render(request, 'movies/movie_not_found.html', status=404)

    movie = movie_data['movie']
    reviews = Review.objects.filter(movie=movie).order_by('-created_at')

    return render(request, 'movies/movie_detail.html', {
        'movie_data': movie_data,
        'movie': movie,
        'reviews': reviews,
    })


def ajax_search_view(request):
    """AJAX endpoint for live search dropdown."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    results = search_movies(query)
    return JsonResponse({
        'results': [
            {
                'id': m['id'],
                'title': m['title'],
                'year': m.get('release_date', '')[:4] if m.get('release_date') else '',
                'poster': TMDB_IMAGE_SMALL + m['poster_path'] if m.get('poster_path') else '',
            }
            for m in results
        ]
    })

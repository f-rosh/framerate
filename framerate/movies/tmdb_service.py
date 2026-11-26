import requests
import time
from django.conf import settings
from .models import Movie

TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'
TMDB_IMAGE_SMALL = 'https://image.tmdb.org/t/p/w92'
TMDB_IMAGE_TRENDING = 'https://image.tmdb.org/t/p/w300'


def _tmdb_get(url, params, retries=2, timeout=10):
    """Internal helper: calls TMDb with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))  # brief backoff
            else:
                raise
    return None


def search_movies(query):
    """Search TMDb for movies matching the query."""
    if not query or len(query.strip()) < 2:
        return []
    try:
        data = _tmdb_get(
            f'{TMDB_BASE_URL}/search/movie',
            params={
                'api_key': settings.TMDB_API_KEY,
                'query': query,
                'include_adult': False,
                'language': 'en-US',
                'page': 1,
            }
        )
        return data.get('results', [])[:10] if data else []
    except (requests.RequestException, TypeError):
        return []


def get_trending_movies(limit=12):
    """Fetch this week's trending movies for the home page."""
    try:
        data = _tmdb_get(
            f'{TMDB_BASE_URL}/trending/movie/week',
            params={'api_key': settings.TMDB_API_KEY, 'language': 'en-US'},
        )
        return data.get('results', [])[:limit] if data else []
    except (requests.RequestException, TypeError):
        return []


def get_movie_detail(tmdb_id):
    """Fetch full movie details. Falls back to DB cache if TMDb fails."""
    # Check DB cache first
    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
    except Movie.DoesNotExist:
        movie = None

    # Try fetching from TMDb
    tmdb_data = None
    try:
        tmdb_data = _tmdb_get(
            f'{TMDB_BASE_URL}/movie/{tmdb_id}',
            params={'api_key': settings.TMDB_API_KEY, 'language': 'en-US'},
        )
    except (requests.RequestException, TypeError):
        pass  # TMDb failed, try DB fallback

    # If TMDb succeeded, cache/update the movie
    if tmdb_data:
        poster_path = tmdb_data.get('poster_path', '')
        poster_url = TMDB_IMAGE_BASE + poster_path if poster_path else ''
        title = tmdb_data.get('title', 'Unknown')

        if movie:
            movie.title = title
            movie.poster_url = poster_url
            movie.save()
        else:
            movie = Movie.objects.create(
                tmdb_id=tmdb_id, title=title, poster_url=poster_url,
            )

        return {
            'movie': movie,
            'poster_url': poster_url,
            'title': title,
            'plot': tmdb_data.get('overview', ''),
            'release_year': tmdb_data.get('release_date', '')[:4] if tmdb_data.get('release_date') else '',
            'runtime': tmdb_data.get('runtime', 0),
            'genres': [g['name'] for g in tmdb_data.get('genres', [])],
            'tmdb_rating': tmdb_data.get('vote_average', 0),
        }

    # TMDb failed - fall back to DB cache if we have it
    if movie:
        return {
            'movie': movie,
            'poster_url': movie.poster_url,
            'title': movie.title,
            'plot': '',
            'release_year': '',
            'runtime': 0,
            'genres': [],
            'tmdb_rating': 0,
        }

    # Neither TMDb nor DB has it
    return None

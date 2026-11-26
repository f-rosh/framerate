"""TMDb discovery helpers for Circle featured movies.

Caches results on the Circle model for ~24h to avoid hammering TMDb.
"""
import time
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from .models import Circle


TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_SMALL = 'https://image.tmdb.org/t/p/w185'

# TMDb canonical genre IDs (English names). Used both by the form (so the
# founder can pick from a dropdown) and by the discover call.
TMDB_GENRES = {
    'Action': 28,
    'Adventure': 12,
    'Animation': 16,
    'Comedy': 35,
    'Crime': 80,
    'Documentary': 99,
    'Drama': 18,
    'Family': 10751,
    'Fantasy': 14,
    'History': 36,
    'Horror': 27,
    'Music': 10402,
    'Mystery': 9648,
    'Romance': 10749,
    'Science Fiction': 878,
    'TV Movie': 10770,
    'Thriller': 53,
    'War': 10752,
    'Western': 37,
}

CACHE_TTL = timedelta(hours=24)


def _tmdb_get(url, params, retries=2, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
            else:
                return None
    return None


def _discover_params(circle):
    """Return the discover params for the circle's topic, or None if N/A."""
    tid = circle.topic_value_id
    if not tid:
        return None

    base = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'en-US',
        'sort_by': 'popularity.desc',
        'page': 1,
        'include_adult': False,
    }

    if circle.topic_type == Circle.GENRE:
        return {**base, 'with_genres': tid}
    if circle.topic_type == Circle.DIRECTOR:
        return {**base, 'with_crew': tid}
    if circle.topic_type == Circle.ACTOR:
        return {**base, 'with_cast': tid}
    if circle.topic_type == Circle.FRANCHISE:
        # Treat topic_value_id as a studio/production-company ID.
        return {**base, 'with_companies': tid}
    return None


def get_featured_movies(circle, force_refresh=False):
    """Return up to 12 popular movies relevant to the circle.

    Results are cached on the Circle instance for ~24h via the
    `featured_cached_at` and `featured_movies` fields.
    """
    if not force_refresh and circle.featured_cached_at and circle.featured_movies:
        age = timezone.now() - circle.featured_cached_at
        if age < CACHE_TTL:
            return circle.featured_movies

    params = _discover_params(circle)
    if not params:
        return circle.featured_movies or []

    data = _tmdb_get(f'{TMDB_BASE_URL}/discover/movie', params)
    if not data:
        return circle.featured_movies or []

    results = []
    for m in data.get('results', [])[:12]:
        poster_path = m.get('poster_path', '')
        results.append({
            'id': m.get('id'),
            'title': m.get('title', 'Unknown'),
            'poster_url': TMDB_IMAGE_SMALL + poster_path if poster_path else '',
            'release_year': (m.get('release_date', '') or '')[:4],
        })

    circle.featured_movies = results
    circle.featured_cached_at = timezone.now()
    circle.save(update_fields=['featured_movies', 'featured_cached_at'])
    return results

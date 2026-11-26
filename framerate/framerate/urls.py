"""
URL configuration for framerate project.
"""

from django.contrib import admin
from django.urls import path, include
from movies import views as movie_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', movie_views.home_view, name='home'),
    path('', include('accounts.urls')),
    path('', include('movies.urls')),
    path('', include('reviews.urls')),
    path('circles/', include('circles.urls')),
]

from django.urls import path
from . import views

urlpatterns = [
    path('review/new/<int:tmdb_id>/', views.write_review_view, name='write_review'),
    path('review/<int:review_id>/edit/', views.edit_review_view, name='edit_review'),
    path('review/<int:review_id>/', views.review_detail_view, name='review_detail'),
    path('review/<int:review_id>/vote/', views.vote_review_view, name='vote_review'),
    path('review/<int:review_id>/comment/', views.add_comment_view, name='add_comment'),
]
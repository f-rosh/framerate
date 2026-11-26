from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from movies.tmdb_service import get_movie_detail
from movies.models import Movie
from .models import Review, Vote, Comment
from .forms import ReviewForm, CommentForm


@login_required
def write_review_view(request, tmdb_id):
    # Try DB first (movie was likely cached when detail page loaded)
    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
    except Movie.DoesNotExist:
        movie_data = get_movie_detail(tmdb_id)
        if not movie_data:
            messages.error(request, "Movie not found.")
            return redirect('home')
        movie = movie_data['movie']

    # Redirect to edit if user already reviewed this movie
    existing = Review.objects.filter(user=request.user, movie=movie).first()
    if existing:
        return redirect('edit_review', review_id=existing.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
            messages.success(request, "Review posted!")
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewForm(user=request.user)

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'movie_data': {
            'title': movie.title,
            'release_year': '',
            'movie': movie,
        },
    })


@login_required
def edit_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        messages.error(request, "You can only edit your own reviews.")
        return redirect('review_detail', review_id=review_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated.")
            return redirect('review_detail', review_id=review_id)
    else:
        form = ReviewForm(instance=review, user=request.user)

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'review': review,
    })


def review_detail_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    comments = review.comments.filter(parent__isnull=True).order_by('created_at')

    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, review=review).first()

    likes = review.votes.filter(vote_type=Vote.LIKE).count()
    dislikes = review.votes.filter(vote_type=Vote.DISLIKE).count()

    comment_form = CommentForm() if request.user.is_authenticated else None

    return render(request, 'reviews/review_detail.html', {
        'review': review,
        'comments': comments,
        'user_vote': user_vote,
        'likes': likes,
        'dislikes': dislikes,
        'comment_form': comment_form,
    })


@login_required
@require_POST
def vote_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    vote_type = request.POST.get('vote_type')

    if vote_type not in [Vote.LIKE, Vote.DISLIKE]:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    existing = Vote.objects.filter(user=request.user, review=review).first()

    if existing:
        if existing.vote_type == vote_type:
            existing.delete()
            action = 'removed'
        else:
            existing.vote_type = vote_type
            existing.save()
            action = 'changed'
    else:
        Vote.objects.create(user=request.user, review=review, vote_type=vote_type)
        action = 'created'

    likes = review.votes.filter(vote_type=Vote.LIKE).count()
    dislikes = review.votes.filter(vote_type=Vote.DISLIKE).count()

    return JsonResponse({
        'action': action,
        'likes': likes,
        'dislikes': dislikes,
        'user_vote': vote_type if action != 'removed' else None,
    })


@login_required
@require_POST
def add_comment_view(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.review = review

        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, review=review)
                comment.parent = parent
            except Comment.DoesNotExist:
                pass

        comment.save()
        messages.success(request, "Comment added.")

    return redirect('review_detail', review_id=review_id)

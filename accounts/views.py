from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignupForm, ProfileEditForm

# Create your views here.
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to FrameRate, {user.username}!")
            return redirect('/')
    else:
        form = SignupForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    
    # Get user's reviews (we'll wire this once reviews app has views)
    reviews = user.review_set.all().order_by('-created_at')[:5]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'reviews': reviews,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_redirect_view(request):
    return redirect('profile', username=request.user.username)
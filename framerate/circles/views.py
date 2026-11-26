from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Circle, CircleMembership
from .forms import CircleCreateForm


def circle_list_view(request):
    circles = Circle.objects.all().order_by('-created_at')
    user_circle_ids = set()
    if request.user.is_authenticated:
        user_circle_ids = set(
            CircleMembership.objects.filter(user=request.user)
            .values_list('circle_id', flat=True)
        )
    return render(request, 'circles/circle_list.html', {
        'circles': circles,
        'user_circle_ids': user_circle_ids,
    })


def circle_detail_view(request, slug):
    circle = get_object_or_404(Circle, slug=slug)
    members = circle.memberships.select_related('user').order_by('-role', 'joined_at')
    reviews = circle.review_set.select_related('user', 'movie').order_by('-created_at')

    is_member = False
    is_founder = False
    if request.user.is_authenticated:
        membership = CircleMembership.objects.filter(
            user=request.user, circle=circle
        ).first()
        is_member = membership is not None
        is_founder = membership is not None and membership.role == CircleMembership.FOUNDER

    return render(request, 'circles/circle_detail.html', {
        'circle': circle,
        'members': members,
        'reviews': reviews,
        'is_member': is_member,
        'is_founder': is_founder,
    })


@login_required
def circle_create_view(request):
    if request.method == 'POST':
        form = CircleCreateForm(request.POST)
        if form.is_valid():
            circle = form.save()
            CircleMembership.objects.create(
                user=request.user, circle=circle, role=CircleMembership.FOUNDER
            )
            messages.success(request, f"Created '{circle.name}'. You're the founder.")
            return redirect('circle_detail', slug=circle.slug)
    else:
        form = CircleCreateForm()
    return render(request, 'circles/circle_form.html', {'form': form})


@login_required
def join_circle_view(request, slug):
    circle = get_object_or_404(Circle, slug=slug)
    membership, created = CircleMembership.objects.get_or_create(
        user=request.user, circle=circle,
        defaults={'role': CircleMembership.MEMBER},
    )
    if created:
        messages.success(request, f"You joined '{circle.name}'.")
    else:
        messages.info(request, "You're already a member.")
    return redirect('circle_detail', slug=slug)


@login_required
def leave_circle_view(request, slug):
    circle = get_object_or_404(Circle, slug=slug)
    membership = CircleMembership.objects.filter(
        user=request.user, circle=circle
    ).first()
    if membership:
        if membership.role == CircleMembership.FOUNDER:
            messages.error(
                request,
                "Founders can't leave their own circle. Delete it via admin if needed.",
            )
        else:
            membership.delete()
            messages.success(request, f"You left '{circle.name}'.")
    return redirect('circle_detail', slug=slug)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.circle_list_view, name='circle_list'),
    path('new/', views.circle_create_view, name='circle_create'),
    path('<slug:slug>/join/', views.join_circle_view, name='join_circle'),
    path('<slug:slug>/leave/', views.leave_circle_view, name='leave_circle'),
    path('<slug:slug>/', views.circle_detail_view, name='circle_detail'),
]

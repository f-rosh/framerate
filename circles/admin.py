from django.contrib import admin
from .models import Circle, CircleMembership

# Register your models here.
@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic_type', 'topic_value', 'is_locked', 'created_at')
    list_filter = ('topic_type', 'is_locked')
    search_fields = ('name', 'topic_value')
    prepopulated_fields = {'slug': ('name',)}    # auto-fills slug from name


@admin.register(CircleMembership)
class CircleMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'circle', 'role', 'joined_at')
    list_filter = ('role',)
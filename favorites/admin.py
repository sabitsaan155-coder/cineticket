from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_title', 'created_at')
    search_fields = ('user__username', 'movie_title')
    list_filter = ('created_at',)

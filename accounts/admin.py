from django.contrib import admin
from django.utils.html import format_html

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'has_avatar', 'id')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('avatar_preview',)
    fields = ('user', 'avatar', 'avatar_preview', 'phone_number', 'bio')

    @admin.display(boolean=True, description='Аватар')
    def has_avatar(self, obj):
        return bool(obj.avatar)

    @admin.display(description='Текущий аватар')
    def avatar_preview(self, obj):
        if not obj.avatar:
            return 'Нет аватара'
        return format_html(
            '<img src="{}" alt="avatar" style="width:60px;height:60px;border-radius:50%;object-fit:cover;" />',
            obj.avatar.url,
        )

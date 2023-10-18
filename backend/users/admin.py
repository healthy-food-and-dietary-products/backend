from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import User


class UserAdmin(admin.ModelAdmin):
    fields = [
        "username",
        "is_staff",
        "is_active",
        "role",
        "first_name",
        "last_name",
        "email",
        "location",
        "birth_date",
        "address",
        "phone_number",
        "photo",
        "preview",
    ]

    list_display = [
        "id",
        "username",
        "is_staff",
        "is_active",
        "role",
        "email",
        "date_joined",
        "last_login",
    ]
    readonly_fields = [
        "preview",
    ]
    search_fields = ("role",)
    ordering = ("id",)

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 200px;">')


admin.site.register(User, UserAdmin)

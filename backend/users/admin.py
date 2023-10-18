from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Address, User


class UserAdmin(admin.ModelAdmin):
    fields = [
        "username",
        "is_staff",
        "is_active",
        "role",
        "first_name",
        "last_name",
        "email",
        "city",
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
    search_fields = [
        "username",
        "role",
    ]
    ordering = [
        "id",
    ]
    list_filter = [
        "username",
        "birth_date",
        "city",
    ]

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 200px;">')


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "country",
        "city",
        "street",
        "house",
        "building",
        "apartment",
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)

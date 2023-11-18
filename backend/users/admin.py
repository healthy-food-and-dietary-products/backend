from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Address, User
from products.admin import UserFavoritesInline


class AddressAdminForm(forms.ModelForm):
    """Form to change widget in AddressInline"""

    class Meta:
        model = Address
        widgets = {"address": forms.TextInput}
        fields = "__all__"


class AddressInline(admin.TabularInline):
    """Inline class to display addresses of a user."""

    model = Address
    form = AddressAdminForm
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Class to display users in admin panel."""

    fields = [
        "username",
        "is_staff",
        "is_active",
        "first_name",
        "last_name",
        "email",
        "city",
        "birth_date",
        "phone_number",
        "photo",
        "preview",
    ]
    list_display = [
        "id",
        "username",
        "is_active",
        "email",
        "birth_date",
        "date_joined",
        "last_login",
    ]
    readonly_fields = ["preview"]
    search_fields = ["username", "email"]
    ordering = ["id"]
    list_filter = ["is_active", "city"]
    inlines = [UserFavoritesInline, AddressInline]

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 200px;">')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Class to display addresses in admin panel."""

    list_display = ["id", "address", "user", "priority_address"]
    search_fields = ["address"]
    list_filter = ["priority_address", "user"]
    ordering = ["id"]

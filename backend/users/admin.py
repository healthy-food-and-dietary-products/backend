from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Address, User
from products.admin import UserFavoritesInline

# class AddressInline(admin.TabularInline):
#     model = Address
#     extra = 1


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
        "phone_number",
        "photo",
        "preview",
        "address",
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
    inlines = [UserFavoritesInline]

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 200px;">')


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "address",
    ]


# @admin.register(UserAddress)
# class UserAddressAdmin(admin.ModelAdmin):
#     list_display = ["id", "user", "address", "priority_address"]
#     fields = ["user", "address", "priority_address"]
#     search_fields = ["user", "address"]
#     ordering = ["id"]
#     list_filter = ["priority_address"]


admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)

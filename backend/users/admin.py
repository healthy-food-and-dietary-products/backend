from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    fields = [
        'username',
        'is_staff',
        'is_active',
        'role',
        'first_name',
        'last_name',
        'email',
        'date_joined',
        'last_login',
        'location',
        'birth_date',
    ]

    list_display = [
        'id',
        'username',
        'is_staff',
        'is_active',
        'role',
        'email',
        'date_joined',
        'last_login',
    ]
    search_fields = ('role',)
    ordering = ('id',)


admin.site.register(User, UserAdmin)

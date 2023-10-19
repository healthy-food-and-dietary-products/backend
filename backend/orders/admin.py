from django.contrib import admin

from orders.models import ShoppingCart


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "status")
    list_editable = ("user", "product", "quantity")
    search_fields = ("user",)

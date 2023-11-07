from django.contrib import admin

from orders.models import Order, ShoppingCart, ShoppingCartProduct


class ShoppingCartProductInline(admin.TabularInline):
    model = ShoppingCartProduct
    list_display = ("id", "product", "quantity")
    list_editable = ("product", "quantity")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    inlines = (ShoppingCartProductInline,)
    list_display = ("id", "user", "status", "total_price")
    list_editable = ("status", "total_price")
    list_filter = ("user", "status")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shopping_cart",
        "ordering_date",
        "status",
        "payment_method",
        "is_paid",
        "delivery_method",
        "comment",
        "address",
        "package",
    )
    list_editable = (
        "payment_method",
        "comment",
        "delivery_method",
        "address",
        "package",
    )
    list_filter = ("ordering_date",)

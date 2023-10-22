from django.contrib import admin

from orders.models import Order, ShoppingCart


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    list_display = ("id", "product", "quantity")
    list_editable = ("product", "quantity", "package")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (ShoppingCartInline,)
    list_display = (
        "id",
        "order_number",
        "user",
        "ordering_date",
        "status",
        "payment_method",
        "is_paid",
        "delivery_method",
        "comment",
        "address"
    )
    list_editable = (
        "payment_method",
        "comment",
        "delivery_method",
        "address"
    )
    list_filter = ("user", "ordering_date", "order_number")

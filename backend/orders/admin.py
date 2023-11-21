from django.contrib import admin

from orders.models import Delivery, Order, OrderProduct


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "delivery_point")
    list_editable = ("delivery_point",)


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    list_display = ("id", "product", "quantity")
    list_editable = ("product", "quantity")


# @admin.register(ShoppingCart)
# class ShoppingCartAdmin(admin.ModelAdmin):
#
#     list_display = ("id", "user", "status", "total_price", "created")
#     list_editable = ("status", "total_price")
#     list_filter = ("user", "status", "created")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderProductInline,)
    list_display = (
        "id",
        "order_number",
        "user",
        "ordering_date",
        "status",
        "payment_method",
        "is_paid",
        "delivery_method",
        "address",
    )
    list_editable = (
        "payment_method",
        "delivery_method",
        "address",
    )
    list_filter = ("status", "ordering_date")

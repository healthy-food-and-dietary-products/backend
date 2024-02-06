from django.contrib import admin

from orders.models import Delivery, Order, OrderProduct


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "delivery_point"]
    list_display_links = ["delivery_point"]


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    list_display = ["id", "product", "quantity"]
    list_editable = ["product", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductInline]
    list_display = [
        "id",
        "order_number",
        "user",
        "ordering_date",
        "status",
        "payment_method",
        "is_paid",
        "delivery_method",
        "total_price",
        "coupon_applied",
        "coupon_discount",
    ]
    list_display_links = ["ordering_date"]
    list_editable = ["payment_method", "delivery_method"]
    list_filter = ["status", "ordering_date"]
    readonly_fields = ["coupon_applied", "coupon_discount"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")

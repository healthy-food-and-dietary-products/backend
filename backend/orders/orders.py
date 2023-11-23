from datetime import datetime, timezone

from django.conf import settings

# from api.orders_serializers import OrderPostDeleteSerializer, OrderProductSerializer
from orders.models import Delivery


class NewOrder(object):
    def __init__(self, request):
        """Initialize the order."""
        self.session = request.session
        self.new_order = self.session.get(settings.ORDER_SESSION_ID, {})

    def save(self):
        self.session[settings.ORDER_SESSION_ID] = self.new_order
        self.session.modified = True

    def create(self, shopping_data, data):
        """Crete the order."""
        delivery = Delivery.objects.get(id=data.get("delivery_point"))
        data = {
            "user_data": data.get("user_data"),
            "products": shopping_data["products"],
            "count_of_products": shopping_data["count_of_products"],
            "total_price": shopping_data["total_price"],
            "payment_method": data.get("payment_method"),
            "delivery_method": data.get("delivery_method"),
            "delivery_point": delivery.delivery_point,
            "address": data.get("address"),
            "comment": data.get("comment"),
            "package": data.get("package"),
            "status": "ORDERED",
            "is_paid": data.get("is_paid"),
            "created_at": int(datetime.now(timezone.utc).timestamp()),
        }

        # serializer = OrderPostDeleteSerializer(data=data)
        # serializer.is_valid(raise_exception=True)# TODO: validate delivery_method
        self.new_order = data
        self.save()

    def get_order_data(self):
        """Iterate over the items in the order."""
        return self.new_order.items()

    def clear(self):
        """remove cart from session."""
        del self.session[settings.ORDER_SESSION_ID]
        self.session.modified = True

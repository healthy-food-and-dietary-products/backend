import random

from django.utils import timezone

from orders.models import Order

LENGTH = 6


def generate_order_number():
    """Generates random ID."""
    time = timezone.localdate()
    random_int = random.randrange(100000, 1000000)
    number = str(time) + "-" + str(random_int)
    if Order.objects.filter(order_number=number):
        number += str(random.randrange(100000, 1000000))
    return number

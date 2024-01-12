import random

from django.utils import timezone

LENGTH = 6


def generate_order_number():
    """Generates random ID."""
    time = timezone.localdate()
    random_int = random.randrange(100000, 1000000)
    return str(time) + "-" + str(random_int)

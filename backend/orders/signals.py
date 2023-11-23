from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from orders.shopping_cart import ShopCart


@receiver(user_logged_in)
def on_login(user, request, **kwargs):
    """
    Перенос корзины пользователя из сессии в БД при входе в систему.
    """
    shopping_cart = ShopCart(request)
    if shopping_cart:
        shopping_cart.make_shopping_cart(user)

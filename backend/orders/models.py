from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User
from products.models import Product

SHOPPINGCART = (('Ordered', 'Передано в заказ'), ('In work','В работе'))

STATUS = (('Ordered', 'Оформлен'), ('In processing', 'В обработке'),
          ('Completed', 'Комплектуется'),
          ('Gathered', 'Собран'),('In delivering', 'Передан в доставку'),
          ('Delivered', 'Доставлен'), ('Completed', 'Завершен'))

PAYMENT_METHODS = (('Cash', 'Наличные'),
                   ('By card on the website', 'Картой на сайте'),
                   ('In getting','При получении'))

DELIVERY_METHOD = (('Point of delivery', 'Пункт выдачи'),
                   ('By courier', 'Курьером'))


class ShoppingCart(models.Model):
    """Model for creating a shopping cart."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Добавил в корзину'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Продукт в корзине'
    )
    quantity = models.IntegerField(
        verbose_name='Количество товара',
        validators=[
                MinValueValidator(1, 'Разрешены значения от 1 до 100'),
                MaxValueValidator(10000, 'Разрешены значения от 1 до 100')
        ]
    )
    status = models.CharField(
        max_length=50,
        choices=SHOPPINGCART,
        default='В работе'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_shopping_cart'
            )
        ]


class Order(models.Model):
    """Model for creating an order."""
    goods = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Покупки'
    )
    date = models.DateField(
        verbose_name='Дата оформления',
        auto_now_add=True
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS,
        default='Оформлен'
        )
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS,
        default='Картой на сайте'
    )
    is_paid = models.BooleanField(default=False)
    comment = models.TextField(
        max_length=400,
        blank=True
    )
    delivery_method = models.CharField(
        max_length=50,
        choices=DELIVERY_METHOD,
        default='Курьером'
    )
    total_price = models.IntegerField(
        default=0
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

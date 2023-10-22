from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models import Product
from users.models import Address, User


class Order(models.Model):
    """Model for creating an order."""

    STATUS = (
        ("Ordered", "Оформлен"),
        ("In processing", "В обработке"),
        ("Completed", "Комплектуется"),
        ("Gathered", "Собран"),
        ("In delivering", "Передан в доставку"),
        ("Delivered", "Доставлен"),
        ("Completed", "Завершен"),
    )

    PAYMENT_METHODS = (
        ("Cash", "Наличные"),
        ("By card on the website", "Картой на сайте"),
        ("In getting by card", "Оплата картой курьеру"),
    )

    DELIVERY_METHOD = (
        ("Point of delivery", "Пункт выдачи"),
        ("By courier", "Курьером"),
    )

    order_number = models.PositiveIntegerField(
        auto_created=True,
        verbose_name="Номер заказа"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Покупатель"
    )
    products = models.ManyToManyField(
        Product,
        through="ShoppingCart",
        through_fields=("order", "product"),
        verbose_name="Продукты в заказе",
    )
    ordering_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оформления заказа"
    )
    status = models.CharField(max_length=50, choices=STATUS,
                              default="Оформлен")
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHODS, default="Картой на сайте"
    )
    is_paid = models.BooleanField(default=False)
    comment = models.TextField(max_length=400, blank=True)
    delivery_method = models.CharField(
        max_length=50, choices=DELIVERY_METHOD, default="Курьером"
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        verbose_name="Адрес покупателя",
        blank=True
    )

    class Meta:
        ordering = ["-ordering_date"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return (f"{self.order_number}: "
                f"{self.user}.")


class ShoppingCart(models.Model):
    """Model for creating a shopping cart."""

    SHOPPINGCART = (("Ordered", "Передано в заказ"), ("In work", "В работе"))
    PACKAGE = (("Add package", "Добавить упаковку"), ("No package", "Без упаковки"))

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Продукт в корзине"
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[
            MinValueValidator(1, 'Разрешены значения от 1 до 10000'),
            MaxValueValidator(10000, 'Разрешены значения от 1 до 10000')
        ]
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Заказ"
    )
    status = models.CharField(
        max_length=50,
        choices=SHOPPINGCART,
        default="В работе"
    )
    package = models.CharField(
        max_length=50,
        choices=PACKAGE,
        verbose_name="Упаковка"
    )

    class Meta:
        verbose_name = "Продукты в корзине"
        verbose_name_plural = "Продукты в заказе"
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_shopping_cart_products'
            )
        ]

    def __str__(self):
        return (f"{self.product.name}: "
                f"{self.product.measure_unit}"
                f"{self.product.price} "
                f"{self.quantity}.")

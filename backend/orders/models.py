from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models import Product
from users.models import Address, User


class ShoppingCart(models.Model):
    """Model for creating a shopping cart."""

    ORDERED = "Передано в заказ"
    INWORK = "В работе"
    SHOPPINGCART = ((ORDERED, "Передано в заказ"), (INWORK, "В работе"))

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Покупатель",
    )
    products = models.ManyToManyField(
        Product,
        through="ShoppingCartProduct",
        through_fields=("shopping_cart", "product"),
        verbose_name="Продукты в корзине",
    )
    status = models.CharField(max_length=50, choices=SHOPPINGCART, default=INWORK)
    total_price = models.PositiveIntegerField(default=0)
    created = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"

    def __str__(self) -> str:
        moment = self.created.strftime("%m/%d/%Y, %H:%M:%S")
        return f"Shopping cart of {self.user}, {self.status}, {moment}"


class ShoppingCartProduct(models.Model):
    """Model for adding products in shopping cart."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Продукт в корзине",
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        default=1,
        validators=[
            MinValueValidator(1, "Разрешены значения от 1 до 10000"),
            MaxValueValidator(10000, "Разрешены значения от 1 до 10000"),
        ],
    )
    shopping_cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Корзина",
    )

    class Meta:
        verbose_name = "Продукты в корзине"
        verbose_name_plural = "Продукты  в корзине"
        constraints = [
            models.UniqueConstraint(
                fields=["shopping_cart", "product"],
                name="unique_shopping_cart_products",
            )
        ]

    def __str__(self):
        return (
            f"{self.product.name}: "
            f"{self.product.measure_unit}"
            f"{self.product.price} "
            f"{self.quantity}."
        )


class Delivery(models.Model):
    """Model for creating delivery."""

    delivery_point = models.CharField(
        max_length=150,
        verbose_name="Пункт выдачи",
    )

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"

    def __str__(self):
        return f"{self.delivery_point}."


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

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Покупатель",
    )
    order_number = models.PositiveIntegerField(default=1, verbose_name="Номер заказа")
    ordering_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата оформления заказа"
    )
    shopping_cart = models.ForeignKey(
        ShoppingCart, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(max_length=50, choices=STATUS, default="Оформлен")
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
        blank=True,
        null=True,
    )
    package = models.BooleanField(default=False, verbose_name="Упаковка")
    delivery_point = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        verbose_name="Пункт выдачи",
    )

    class Meta:
        ordering = ["-ordering_date"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.ordering_date} , {self.order_number} ,{self.user.username}."

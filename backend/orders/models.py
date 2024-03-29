from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models import Coupon, Product
from users.models import Address, User


# TODO: seems this model is not used now (all shopcarts are in sessions)
class ShoppingCart(models.Model):
    """Model for creating a shopping cart."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Покупатель",
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Продукт в корзине",
    )
    created = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"

    def __str__(self) -> str:
        moment = self.created.strftime("%m/%d/%Y, %H:%M:%S")
        return f"Shopping cart of {self.user}, {self.status}, {moment}"


class Delivery(models.Model):
    """Model to store pick-up points addresses."""

    delivery_point = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Пункт выдачи",
    )

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"

    def __str__(self):
        return self.delivery_point


class Order(models.Model):
    """Model for creating an order."""

    ORDERED = "Ordered"
    PROCESSED = "In processing"
    COLLECTING = "Collecting"
    GATHERED = "Gathered"
    DELIVERING = "In delivering"
    DELIVERED = "Delivered"
    COMPLETED = "Completed"

    STATUS = (
        (ORDERED, "Оформлен"),
        (PROCESSED, "В обработке"),
        (COLLECTING, "Комплектуется"),
        (GATHERED, "Собран"),
        (DELIVERING, "Передан в доставку"),
        (DELIVERED, "Доставлен"),
        (COMPLETED, "Завершен"),
    )

    DELIVERY_POINT_PAYMENT = "Payment at the point of delivery"
    COURIER_CASH_PAYMENT = "In getting by cash"
    ONLINE_PAYMENT = "Online"

    PAYMENT_METHODS = (
        (DELIVERY_POINT_PAYMENT, "Оплата в пункте самовывоза"),
        (COURIER_CASH_PAYMENT, "Оплата наличными курьеру"),
        (ONLINE_PAYMENT, "Оплата на сайте"),
    )

    DELIVERY_POINT = "Point of delivery"
    COURIER = "By courier"

    DELIVERY_METHOD = ((DELIVERY_POINT, "Пункт выдачи"), (COURIER, "Курьер"))

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="orders",
        verbose_name="Покупатель",
    )
    order_number = models.CharField("Number", max_length=50, default="1")
    ordering_date = models.DateTimeField(auto_now_add=True, verbose_name="DateTime")
    products = models.ManyToManyField(
        Product,
        through="OrderProduct",
        through_fields=("order", "product"),
        verbose_name="Продукты в заказе",
        related_name="orders",
    )
    status = models.CharField("Status", max_length=50, choices=STATUS, default=ORDERED)
    payment_method = models.CharField(
        "Payment Method",
        max_length=50,
        choices=PAYMENT_METHODS,
        default=COURIER_CASH_PAYMENT,
    )
    is_paid = models.BooleanField("Is paid", default=False)
    comment = models.TextField("Comment", null=True, blank=True)
    delivery_method = models.CharField(
        "Delivery Method", max_length=50, choices=DELIVERY_METHOD, default=COURIER
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="User's address",
        related_name="orders",
    )
    package = models.FloatField(
        "Package price",
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Price per order packaging",
    )
    delivery_point = models.ForeignKey(
        Delivery,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Delivery Point",
        related_name="orders",
    )
    add_address = models.CharField(
        max_length=450, blank=True, null=True, verbose_name="Add address"
    )
    user_data = models.CharField(
        max_length=450, blank=True, null=True, verbose_name="Anonimus user's data"
    )
    total_price = models.FloatField(
        blank=True, null=True, verbose_name="Order's total_price"
    )
    coupon_applied = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders",
        verbose_name="Coupon",
    )
    coupon_discount = models.PositiveSmallIntegerField(
        "Coupon %", validators=[MaxValueValidator(100)], blank=True, null=True
    )

    class Meta:
        ordering = ["-ordering_date"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        if self.user is not None:
            return f"Order {self.order_number} of {self.user.username}"
        return f"Order {self.order_number} of Anonymous User"


class OrderProduct(models.Model):
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
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Заказ",
    )

    class Meta:
        verbose_name = "Продукты в заказе"
        verbose_name_plural = "Продукты  в заказе"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_order_products",
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.order.pk}."

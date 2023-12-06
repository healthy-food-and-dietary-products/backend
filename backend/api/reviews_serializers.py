from rest_framework import serializers

from orders.models import OrderProduct
from products.models import Product
from reviews.models import Review

REVIEW_MULTIPLE_ERROR_MESSAGE = "Вы можете оставить только один отзыв на этот продукт."
REVIEW_NO_ORDER_ERROR_MESSAGE = (
    "Вы не можете оценивать продукт, которого нет в вашей Истории заказов."
)


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews representation."""

    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)
    was_edited = serializers.BooleanField(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "author", "product", "score", "pub_date", "was_edited", "text")

    def validate(self, data):
        super().validate(data)
        if self.context["request"].method != "POST":
            return data
        user = self.context["request"].user
        product_id = self.context["request"].parser_context["kwargs"]["product_id"]
        product = Product.objects.get(id=product_id)
        if Review.objects.filter(author=user, product=product).exists():
            raise serializers.ValidationError(REVIEW_MULTIPLE_ERROR_MESSAGE)
        if not OrderProduct.objects.filter(product=product, order__user=user).exists():
            raise serializers.ValidationError(REVIEW_NO_ORDER_ERROR_MESSAGE)
        return data

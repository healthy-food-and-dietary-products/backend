from rest_framework import serializers

from reviews.models import Review

REVIEW_ERROR_MESSAGE = "Вы можете оставить только один отзыв на этот продукт."


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews representation."""

    author = serializers.SlugRelatedField(slug_field="username", read_only=True)
    product = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "author", "product", "score", "pub_date", "was_edited", "text")

    def validate(self, data):
        super().validate(data)
        if self.context["request"].method != "POST":
            return data
        user = self.context["request"].user
        product_id = self.context["request"].parser_context["kwargs"]["product_id"]
        if Review.objects.filter(author=user, product__id=product_id).exists():
            raise serializers.ValidationError(REVIEW_ERROR_MESSAGE)
        return data

from rest_framework import serializers

from products.models import Category, Component, Producer, Promotion, Subcategory, Tag


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories representation."""

    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class SubcategorySerializer(serializers.ModelSerializer):
    """Serializer for subcategories representation."""

    class Meta:
        model = Subcategory
        fields = ("id", "parent_category", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags representation."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class ComponentSerializer(serializers.ModelSerializer):
    """Serializer for components representation."""

    class Meta:
        model = Component
        fields = ("id", "name")


class ProducerSerializer(serializers.ModelSerializer):
    """Serializer for produsers representation."""

    class Meta:
        model = Producer
        fields = ("id", "name", "producer_type", "description", "address")


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for promotions representation."""

    class Meta:
        model = Promotion
        fields = (
            "id",
            "promotion_type",
            "name",
            "discount",
            "conditions",
            "is_active",
            "is_constant",
            "start_time",
            "end_time",
        )

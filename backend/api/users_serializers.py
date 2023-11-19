from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserDeleteSerializer as DjoserUserDeleteSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Address
from users.utils import city_choices

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for addresses representation."""

    class Meta:
        model = Address
        fields = ("id", "address", "priority_address")


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Serializer for creating users."""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    city = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "password", "city")
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "password": {"required": True},
        }

    @extend_schema_field(str)
    def get_city(self, obj):
        return city_choices[0][0]


class UserSerializer(DjoserUserSerializer):
    """Serializer for displaying and updating users."""

    addresses = AddressSerializer(many=True, required=False)
    address_quantity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "city",
            "birth_date",
            "addresses",
            "address_quantity",
            "phone_number",
            "photo",
        )

    @extend_schema_field(int)
    def get_address_quantity(self, obj):
        return obj.addresses.count()

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get("addresses") is not None:
            addresses = validated_data.pop("addresses")
            priority_count = 0
            for existing_address in instance.addresses.all():
                existing_address.delete()
            for address_dict in addresses:
                if not instance.addresses.filter(address=address_dict["address"]):
                    Address.objects.create(
                        address=address_dict["address"],
                        user=instance,
                        priority_address=address_dict.get("priority_address", False),
                    )
                    priority_count += address_dict.get("priority_address", False)
                    if priority_count > 1:
                        raise serializers.ValidationError(
                            "Разрешен только один приоритетный адрес."
                        )
        for field in validated_data:
            setattr(instance, field, validated_data[field])
        instance.save()
        return instance


class UserLightSerializer(UserSerializer):
    """Serializer to represent user in favorite products serializers."""

    class Meta(UserSerializer.Meta):
        fields = ("username", "email")


class CustomUserDeleteSerializer(DjoserUserDeleteSerializer):
    """Serializer to delete users without input of current password."""

    current_password = serializers.ReadOnlyField()

from collections import OrderedDict

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
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

    def to_representation(self, instance):
        new_repr = OrderedDict()
        new_repr["address"] = instance.address
        new_repr["priority_address"] = instance.priority_address
        return new_repr


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

    def get_address_quantity(self, obj):
        return obj.addresses.count()

    def update(self, instance, validated_data):
        if not validated_data.get("addresses"):
            return instance
        addresses = validated_data.pop("addresses")
        for existing_address in instance.addresses.all():
            existing_address.delete()
        for address_dict in addresses:
            if not instance.addresses.filter(address=address_dict["address"]):
                Address.objects.create(
                    address=address_dict["address"],
                    user=instance,
                    priority_address=address_dict["priority_address"],
                )
        return instance


class UserLightSerializer(UserSerializer):
    """Serializer to represent user in favorite products serializers."""

    class Meta(UserSerializer.Meta):
        fields = ("username", "email")

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Address
from users.utils import city_choices

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "address", "priority_address")


class UserCreateSerializer(UserCreateSerializer):
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
    # address = serializers.SerializerMethodField()
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
            # "address",
            "address_quantity",
            "phone_number",
            "photo",
        )

    def get_address(self, obj):
        return obj.addresses.all()

    def get_address_quantity(self, obj):
        return obj.addresses.count()


class UserLightSerializer(UserSerializer):
    """Serializer to represent user in favorite products serializers."""

    class Meta(UserSerializer.Meta):
        fields = ("username", "email")

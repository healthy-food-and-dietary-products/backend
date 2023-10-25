from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from users.models import User


class UserSerializer(UserSerializer):
    address = AddressSerializer(many=True)
    address_quantity = serializers.SerializerMethodField()
    photo = Base64ImageField()
    

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "city",
            "birth_date",
            # 'address',
            "address_quantity",
            "phone_number",
            "photo",
        )

    def get_address_quantity(self, obj):
        # obj.user_addresses.count()
        return pass

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
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

from rest_framework import response, status

from .users_serializers import CustomUserDeleteSerializer, UserSerializer


class DestroyWithPayloadMixin(object):
    """Mixin to provide detailed api response after delete requests."""

    def destroy(self, *args, **kwargs):
        if isinstance(self.get_serializer(), CustomUserDeleteSerializer):
            serializer_data = UserSerializer(self.get_object()).data
        else:
            serializer_data = self.get_serializer(self.get_object()).data
        serializer_data["Success"] = "This object was successfully deleted"
        super().destroy(*args, **kwargs)
        return response.Response(serializer_data, status=status.HTTP_200_OK)

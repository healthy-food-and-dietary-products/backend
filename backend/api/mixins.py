from rest_framework import response, status

from .users_serializers import CustomUserDeleteSerializer, UserSerializer

MESSAGE_ON_DELETE = "This object was successfully deleted"


class DestroyWithPayloadMixin(object):
    """Mixin to provide detailed api response after delete requests."""

    def destroy(self, *args, **kwargs):
        if isinstance(self.get_serializer(), CustomUserDeleteSerializer):
            serializer_data = UserSerializer(self.get_object()).data
        else:
            serializer_data = self.get_serializer(self.get_object()).data
        # TODO: make special serializer having success field,
        # add this new serializer to all swagger decorators instead of MESSAGE_ON_DELETE
        serializer_data["Success"] = MESSAGE_ON_DELETE
        super().destroy(*args, **kwargs)
        return response.Response(serializer_data, status=status.HTTP_200_OK)

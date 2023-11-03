from rest_framework import response, status


class DestroyWithPayloadMixin(object):
    def destroy(self, *args, **kwargs):
        serializer_data = self.get_serializer(self.get_object()).data
        serializer_data["Success"] = "This object was successfully deleted"
        super().destroy(*args, **kwargs)
        return response.Response(serializer_data, status=status.HTTP_200_OK)

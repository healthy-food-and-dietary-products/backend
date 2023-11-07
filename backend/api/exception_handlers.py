from rest_framework import status
from rest_framework.views import exception_handler


def custom_404_exception_handler(exc, context):
    """Custom response for 404 status code."""
    response = exception_handler(exc, context)
    if response and response.status_code == status.HTTP_404_NOT_FOUND:
        response.data["detail"] = "An object with this ID does not exist"
    return response

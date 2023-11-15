from drf_standardized_errors.handler import exception_handler
from rest_framework import status


def custom_404_exception_handler(exc, context):
    """Custom response for 404 status code."""
    response = exception_handler(exc, context)
    if response and response.status_code == status.HTTP_404_NOT_FOUND:
        response.data[
            "detail"
        ] = "An object or objects combination with this ID does not exist"
    return response

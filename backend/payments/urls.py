from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("pay/<int:pk>/", views.OrderPayView.as_view(), name="pay"),
    path("config/", views.stripe_config),
    path(
        "create-checkout-session/<int:order_id>/",
        views.create_checkout_session,
        name="create-checkout-session",
    ),
    path("payment-good/", views.SuccessView.as_view()),
    path("payment-bad/", views.CancelledView.as_view()),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe-webhook"),
]

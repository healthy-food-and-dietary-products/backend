import stripe
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from api.orders_views import (
    PAY_ALREADY_PAID_ORDER_ERROR_MESSAGE,
    PAY_SOMEONE_ELSE_ORDER_ERROR_MESSAGE,
    STRIPE_SESSION_CREATE_ERROR_MESSAGE,
)
from core.loggers import logger
from orders.models import Order


class OrderPayView(TemplateView):
    """Go to the payment page."""

    def get(self, request, **kwargs):
        template = "home.html"
        user = self.request.user
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.is_paid is True:
            return JsonResponse(
                {"errors": PAY_ALREADY_PAID_ORDER_ERROR_MESSAGE.format(pk=order.pk)},
                json_dumps_params={"ensure_ascii": False},
            )
        if order.user is not None and order.user != user:
            return JsonResponse(
                {
                    "errors": PAY_SOMEONE_ELSE_ORDER_ERROR_MESSAGE.format(
                        pk=order.pk, user=request.user
                    )
                },
                json_dumps_params={"ensure_ascii": False},
            )
        return render(request, template, {"order": order})


@csrf_exempt
def stripe_config(request):
    """Checking the configuration."""
    if request.method == "POST":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    return None


@csrf_exempt
def create_checkout_session(request, order_id):
    """Get an order and pay."""
    order = get_object_or_404(Order, pk=order_id)
    if request.method == "POST":
        domain_url = f"http://{get_current_site(request)}/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "rub",
                            "product_data": {
                                "name": order,
                            },
                            "unit_amount": int(order.total_price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                success_url=domain_url + "success",
                cancel_url=domain_url + "cancel",
                client_reference_id=request.user.username
                if request.user.is_authenticated
                else None,
                payment_method_types=["card"],
                mode="payment",
                metadata={"order_id": order.id},
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return JsonResponse(
                {"message": STRIPE_SESSION_CREATE_ERROR_MESSAGE, "errors": str(e)}
            )
    return None


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook view to handle checkout session completed event
    (payment verification).
    """
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)  # TODO: shows success page in this case, fix it
    if event["type"] == "checkout.session.completed":
        logger.info("Payment was successful.")
        order_id = event["data"]["object"]["metadata"]["order_id"]
        order = get_object_or_404(Order, pk=order_id)
        order.is_paid = True
        order.save()
    return HttpResponse(
        status=200,
    )


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelledView(TemplateView):
    template_name = "cancel.html"

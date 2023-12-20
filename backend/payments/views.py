import stripe
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from orders.models import Order


class OrderPayView(TemplateView):
    """Go to the payment page."""

    def get(self, request, **kwargs):
        template = "home.html"
        user = self.request.user
        order = get_object_or_404(Order, id=self.kwargs.get("pk"))
        if order.user is not None and order.user != user:
            raise PermissionDenied()  # TODO: don't make django down
        return render(request, template)


@csrf_exempt
def stripe_config(request):
    """Checking the configuration."""
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    return None


@csrf_exempt
def create_checkout_session(request):
    """Payment"""
    user = request.user
    order = Order.objects.filter(user=user.id).first()
    massage = f"Заказ № {order.order_number} пользователя {str(request.user)}"
    if request.method == "GET":
        domain_url = f"http://{get_current_site(request)}/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "rub",
                            "product_data": {
                                "name": massage,
                            },
                            "unit_amount": int(order.total_price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancelled/",
                client_reference_id=user.id if user.is_authenticated else None,
                payment_method_types=["card"],
                mode="payment",
            )
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})
    return None


@csrf_exempt
def stripe_webhook(request):
    """Payment verification"""
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")
        user = request.user
        order = Order.objects.filter(user=user.id).first()
        order.is_paid = "True"
        order.save()
    return HttpResponse(status=200)


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelledView(TemplateView):
    template_name = "cancel.html"

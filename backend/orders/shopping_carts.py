from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from core.loggers import logger
from products.models import Coupon, Product

PRICE_DECIMAL_PLACES = 2


class ShopCart(object):
    def __init__(self, request):
        """Initialize the shopping_cart."""
        self.session = request.session
        self.shopping_cart = self.session.get(settings.SHOPPING_CART_SESSION_ID, {})
        self.coupon_id = self.session.get("coupon_id")
        self.request = request

    def save(self):
        self.session[settings.SHOPPING_CART_SESSION_ID] = self.shopping_cart
        self.session.modified = True

    def add(self, product, quantity):
        """Add a product to the shopping_cart."""
        p_id = str(product["id"])
        p = Product.objects.get(id=product["id"])
        current_site = get_current_site(self.request)
        if settings.MODE == "dev" or current_site.domain == "localhost":
            domain_media_url = f"http://{current_site}/media/"
        else:
            domain_media_url = f"https://{current_site}/media/"
        if p_id not in self.shopping_cart:
            self.shopping_cart[p_id] = {
                "id": p.id,
                "name": p.name,
                "photo": domain_media_url + str(p.photo),
                "category": p.category.slug,
                "quantity": quantity,
                "final_price": p.final_price,
                "created_at": timezone.localtime().isoformat(),
                "amount": p.amount,
                "measure_unit": p.measure_unit,
            }
        else:
            self.shopping_cart[p_id]["quantity"] = int(quantity)

        self.save()

    def remove(self, product_id):
        """Change a product quantity from the shopping_cart."""
        p_id = str(product_id)
        del self.shopping_cart[p_id]
        self.save()

    def __iter__(self):
        """Iterate over the items in the cart and get the products from the database."""
        for item in self.shopping_cart.values():
            item["id"] = item["id"]
            item["name"] = item["name"]
            item["photo"] = item["photo"]
            item["final_price"] = item["final_price"]
            item["quantity"] = int(item["quantity"])
            item["total_price"] = round(
                item["quantity"] * item["final_price"], PRICE_DECIMAL_PLACES
            )
            item["category"] = item.get("category", None)
            item["amount"] = item.get("amount")
            item["measure_unit"] = item.get("measure_unit")
            item["created_at"] = item["created_at"]

            yield item

    def get_shop_products(self):
        """List of all products in the cart."""
        products = []
        for item in self.shopping_cart.values():
            product = {}
            product["id"] = item["id"]
            product["name"] = item["name"]
            product["photo"] = item["photo"]
            product["quantity"] = item["quantity"]
            product["category"] = item["category"]
            product["amount"] = item["amount"]
            product["measure_unit"] = item["measure_unit"]
            products.append(product)
        return products

    def __len__(self):
        """Count all items in the cart."""
        return sum(int(item["quantity"]) for item in self.shopping_cart.values())

    def get_coupon(self):
        if not self.coupon_id:
            return None
        try:
            return Coupon.objects.get(id=self.coupon_id)
        except Coupon.DoesNotExist:
            self.coupon_id = None
            return None

    def get_total_price_without_coupon(self):
        return sum(
            int(item["quantity"]) * item["final_price"]
            for item in self.shopping_cart.values()
        )

    def get_coupon_shopping_cart_discount(self, coupon, total_price_without_coupon):
        if coupon:
            shopping_cart_discount = total_price_without_coupon * coupon.discount / 100
            return round(shopping_cart_discount, PRICE_DECIMAL_PLACES)
        return 0

    def get_total_price(self, coupon):
        total_price = self.get_total_price_without_coupon()
        if coupon:
            discount = self.get_coupon_shopping_cart_discount(coupon, total_price)
            logger.info(f"Promocode was applied, the discount is {discount}.")
            return round(total_price - discount, PRICE_DECIMAL_PLACES)
        return round(total_price, PRICE_DECIMAL_PLACES)

    def clear(self):
        """remove cart from session."""
        del self.session[settings.SHOPPING_CART_SESSION_ID]
        self.session.modified = True

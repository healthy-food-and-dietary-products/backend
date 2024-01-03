from django.conf import settings
from django.utils import timezone

from products.models import Product


class ShopCart(object):
    def __init__(self, request):
        """Initialize the shopping_cart."""
        self.session = request.session
        self.shopping_cart = self.session.get(settings.SHOPPING_CART_SESSION_ID, {})

    def save(self):
        self.session[settings.SHOPPING_CART_SESSION_ID] = self.shopping_cart
        self.session.modified = True

    def add(self, product, quantity):
        """Add a product to the shopping_cart."""
        p_id = str(product["id"])
        p = Product.objects.get(id=product["id"])
        if p_id not in self.shopping_cart:
            self.shopping_cart[p_id] = {
                "id": p.id,
                "name": p.name,
                "photo": str(p.photo),
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
            item["total_price"] = round(item["quantity"] * item["final_price"], 2)
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

    def get_total_price(self):
        return round(
            sum(
                int(item["quantity"]) * item["final_price"]
                for item in self.shopping_cart.values()
            ),
            2,
        )

    def clear(self):
        """remove cart from session."""
        del self.session[settings.SHOPPING_CART_SESSION_ID]
        self.session.modified = True

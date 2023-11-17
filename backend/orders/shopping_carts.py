from datetime import datetime, timezone

from django.conf import settings

from products.models import Product


class ShopCart(object):
    def __init__(self, request):
        """
        Initialize the shopping_cart.
        """
        self.session = request.session
        shopping_cart = self.session.get(settings.SHOPPING_CART_SESSION_ID)
        if not shopping_cart:
            shopping_cart = self.session[settings.SHOPPING_CART_SESSION_ID] = {}
        self.shopping_cart = shopping_cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        p = Product.objects.get(id=product["id"])
        if product["id"] not in self.shopping_cart.keys():
            self.shopping_cart[product["id"]] = {
                "name": p.name,
                "quantity": product["quantity"],
                "final_price": p.final_price,
                "created_at": int(datetime.now(timezone.utc).timestamp() * 1000),
            }
        if update_quantity:
            self.shopping_cart[product["id"]]["quantity"] = quantity

        self.save()

    def save(self):
        self.session[settings.SHOPPING_CART_SESSION_ID] = self.shopping_cart
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart
        :param product:
        :return:
        """
        product_id = str(product.id)
        if product_id in self.shopping_cart:
            del self.shopping_cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.shopping_cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.shopping_cart.copy()
        for product in products:
            cart[product.id]["name"] = product.name
            cart[product.id]["final_price"] = product.final_price

        for item in cart.values():
            item["name"] = item["name"]
            item["quantity"] = int(item["quantity"])
            item["total_price"] = item["quantity"] * item["final_price"]

            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(int(item["quantity"]) for item in self.shopping_cart.values())

    def get_total_price(self):
        print(self.shopping_cart.values())
        return sum(
            item["quantity"] * item["final_price"] for item in self.shopping_cart.values()
        )

    def clear(self):
        """
        remove cart from session
        :return:
        """
        del self.session[settings.SHOPPING_CART_SESSION_ID]
        self.session.modified = True

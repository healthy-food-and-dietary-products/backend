from decimal import Decimal

from django.conf import settings

from products.models import Product
from orders.models import ShoppingCartProduct, ShoppingCart

DECIMAL_PLACES_NUMBER = 2


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
        product_id = str(product.id)
        if product_id not in self.shopping_cart:
            self.shopping_cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.shopping_cart[product_id]['quantity'] = quantity
        else:
            self.shopping_cart[product_id]['quantity'] += quantity

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
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.shopping_cart[str(product.id)]['product'] = product

        for item in self.shopping_cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.shopping_cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.shopping_cart.values())

    def clear(self):
        """
        remove cart from session
        :return:
        """
        del self.session[settings.SHOPPING_CART_SESSION_ID]
        self.session.modified = True

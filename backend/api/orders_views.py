from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import filters, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .users_serializers import UserSerializer
from orders.models import ShoppingCart, ShoppingCartProduct, Order
from products.models import Product
from users.models import User
from .permissions import IsAuthorOnly
from .orders_serializers import (
    ShoppingCartGetSerializer,
    ShoppingCartPostUpdateDeleteSerializer,
    OrderPostDeleteSerializer,
    OrderListSerializer,
)


class CustomUserViewSet(ModelViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer



# 
# class ShoppingCartViewSet(ModelViewSet):
#     """Viewset for shopping_cart."""
#     queryset = ShoppingCart.objects.all()
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['get', 'post', 'patch', 'delete']
# 
#     def get_serializer_class(self):
#         if self.action in ("list", "retrieve"):
#             return ShoppingCartGetSerializer
#         return ShoppingCartPostUpdateDeleteSerializer


    
    @action(detail=True, methods=["post"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        """Method for add/update/delete the shopping_cart."""
        print(request.data)
        products = request.data["products"]
        user = request.user

        shop_cart = ShoppingCart.objects.filter(
            user=user,
            status="В работе",
        )
        if shop_cart:
            raise ValueError(
                'Ваша корзина еще не оформлена, можно добавить продукты или изменить!')
        serializer = ShoppingCartPostUpdateDeleteSerializer(
            data={'user': user.id, 'products': products},
            context={"request": request.data})
        serializer.is_valid(raise_exception=True)
        shopping_cart = ShoppingCart.objects.create(
            products, user=self.context["request"].user
        )
        ShoppingCartProduct.objects.bulk_create(
            [
                    ShoppingCartProduct(
                        shopping_cart=shopping_cart,
                        quantity=product["quantity"],
                        product=Product.objects.get(id=product["id"]),
                    )
                    for product in products
            ]
        )
        print(serializer.data, "?????????????????????????????")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        


    @action(detail=True, methods=['get', "patch", 'delete'],
            permission_classes=[IsAuthorOnly])
    def shopping_cart(self, request, **kwargs):
        """Method for getting the shopping_cart."""
        author = get_object_or_404(User, id=kwargs['pk'])
        user = request.user
        products = request.data["products"]

        if request.method == 'GET':
            shopping_cart = ShoppingCart.objects.filter(
                    user=user,
                    status="В работе")
            print(user, ">>>>>>>>>>>>>>>>>")
            if not shopping_cart:
                return Response("В вашей корзине нет товаров, наполните ее.",
                                status=status.HTTP_200_OK)

            serializer = ShoppingCartGetSerializer(
                data={'user': user.id},
                context={"request": request.data},)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            partial = kwargs.pop('partial', False)
            product = get_object_or_404(Product, id=kwargs['id'])
            user = request.user
            serializer = ShoppingCartPostUpdateSerializer(
                data={'user': user.id, 'product': product['product']},
                context={"request": request.data}, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
        elif request.method == 'DELETE':
            product = get_object_or_404(Product, id=kwargs['id'])
            shopping_cart = ShoppingCart.objects.filter(
                product=product.id, user=user.id)
            if not shopping_cart:
                return Response({'errors': 'Корзина пуста!'},
                                status=status.HTTP_400_BAD_REQUEST)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


        

class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset for Order."""

    queryset = Order.objects.all()
    permission_classes = (AllowAny,)
    # permission_classes = (IsAuthenticated, IsAuthorOnly)
    http_method_names = ["get", "post", "delete"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return OrderListSerializer
        return OrderPostDeleteSerializer

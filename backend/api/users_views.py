<<<<<<< HEAD

# from django.shortcuts import get_object_or_404
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework import viewsets, filters
# from rest_framework.decorators import api_view, permission_classes, action
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from users.models import User
# # from .permissions import Admin, Superuser
# from .users_serializers import UserSerializer
# # from .serializers import TokenSerializer, UserSelfSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     """Получить список всех пользователей или добавить пользователя."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     http_method_names = ['get', 'post', 'patch', 'delete']
#     # permission_classes = [Admin | Superuser]

#     @action(
#         detail=False,
#         methods=['get', 'patch'],
#         permission_classes=[IsAuthenticated]
#     )
#     def me(self, request):
#         user = request.user
#         serializer_class = UserSerializer

#         if request.method == 'GET':
#             serializer = serializer_class(user)
#             return Response(serializer.data)

#         serializer = serializer_class(user, partial=True, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response(serializer.errors)


# # @api_view(['POST'])
# # @permission_classes([AllowAny])
# # def signup(request):
# #     serializer = SignUpSerializer(data=request.data)
# #     email = request.data.get('email')
# #     username = request.data.get('username')
# #     user = CustomUser.objects.filter(username=username, email=email).exists()
# #     if not user:
# #         serializer.is_valid(raise_exception=True)
# #         serializer.save()
# #         user = CustomUser.objects.get(username=username, email=email)
# #         confirmation_code = default_token_generator.make_token(user)
# #         send_confirmation_code(email, confirmation_code, username)
# #         return Response(serializer.data, status=status.HTTP_200_OK)
# #     return Response('Пользователь создан!', status=status.HTTP_200_OK)


# # @api_view(['POST'])
# # @permission_classes([AllowAny])
# # def token(request):
# #     serializer = TokenSerializer(data=request.data)
# #     serializer.is_valid(raise_exception=True)
# #     username = request.data.get('username')
# #     user = get_object_or_404(CustomUser, username=username)
# #     confirmation_code = request.data.get('confirmation_code')
# #     if default_token_generator.check_token(user, confirmation_code):
# #         token = get_tokens_for_user(user)
# #         response = {'token': str(token['access'])}
# #         return Response(response, status=status.HTTP_200_OK)
# #     return Response('Проверочный код не совпал',
# #                     status=status.HTTP_400_BAD_REQUEST)
=======
>>>>>>> develop

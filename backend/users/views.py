from rest_framework.views import APIView
from rest_framework.response import Response
import requests


class UserActivationView(APIView):
    def get (self, request, uid, token):
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/api/users/activate/"
        post_data = {'uid': uid, 'token': token}
        result = requests.post(post_url, data = post_data)
        content = result.text
        return Response(content)




# from rest_framework import permissions
# from rest_framework.decorators import (
#     api_view,
#     permission_classes,
# )
# from rest_framework.response import Response
# from rest_framework.views import APIView

# import requests

# from django.views.generic import DetailView, UpdateView, CreateView, View, TemplateView
# from django.db import transaction
# from django.urls import reverse_lazy
# from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView 
# from django.contrib.sites.models import Site
# from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes
# from django.core.mail import send_mail
# from django.shortcuts import redirect
# from django.contrib.auth import login

# from .models import Profile


# from django.dispatch import receiver

# from djoser.signals import user_activated

# # @receiver(user_activated)
# # def my_handler(user, request):
# #     # do what you need here


# @receiver(user_activated)
# @api_view(["GET"])
# @permission_classes([permissions.AllowAny])
# def request_user_activation(request, uid, token):
#     """ 
#     Intermediate view to activate a user's email.
#     """
#     # post_url = "http://127.0.0.1:8000/user_activated"
#     post_url = "http://127.0.0.1:8000/users/activation/"
    
#     post_data = {"uid": uid, "token": token}
#     result = requests.post(post_url, data=post_data)
#     content = result.text
#     return Response(content)

# # User = get_user_model()


# # class UserConfirmEmailView(View):
# #     def get(self, request, uidb64, token):
# #         try:
# #             uid = urlsafe_base64_decode(uidb64)
# #             user = User.objects.get(pk=uid)
# #         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
# #             user = None

# #         if user is not None and default_token_generator.check_token(user, token):
# #             user.is_active = True
# #             user.save()
# #             login(request, user)
# #             return redirect('email_confirmed')
# #         else:
# #             return redirect('email_confirmation_failed')

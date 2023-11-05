import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class ActivateUser(GenericAPIView):
    def get(self, request, uid, token, format=None):
        protocol = "https://" if request.is_secure() else "http://"
        web_url = protocol + request.get_host()
        post_url = web_url + "/api/users/activation/"
        post_data = {"uid": uid, "token": token}
        response = requests.post(post_url, data=post_data)
        if response.status_code == 204:
            return Response({"Ваш аккаунт активирован."}, response.status_code)
        return Response({"Ссылка устарела."}, response.status_code)

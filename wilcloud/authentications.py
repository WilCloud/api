from wilcloud_user.models import  Apikey
from rest_framework.authentication import BaseAuthentication, SessionAuthentication as BaseSessionAuthentication


class SessionAuthentication(BaseSessionAuthentication):

    def enforce_csrf(self, request):
        return

    def authenticate(self, request):
        return super().authenticate(request)


class ApikeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        secret = request.META.get('HTTP_AUTHORIZATION')

        if not secret:
            return None

        apikey = Apikey.objects.filter(secret=secret)

        if apikey.exists():
            return (apikey.first().user, None)
        return None

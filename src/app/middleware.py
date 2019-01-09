from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import TokenAuthentication


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


class UserMiddleware(SimpleMiddleware):
    """Basic middleware to add user to request with some non-django authentication methods, like JWT or DRF token"""
    def __call__(self, request):
        if not request.user.is_authenticated:
            request.user = SimpleLazyObject(lambda: self.get_user(request) or get_user(request))  # try ours get_user(), if fails -- django's stock one

        return self.get_response(request)


class TokenAuthMiddleware(UserMiddleware):
    @staticmethod
    def get_user(request):
        token_authentication = TokenAuthentication()
        auth = token_authentication.authenticate(request)

        if auth is not None:
            return auth[0]

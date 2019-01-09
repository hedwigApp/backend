from rest_framework.response import Response

from a12n.api.serializers import UserFastSerializer
from app.views import LoginRequiredAPIView


class WhoAmIView(LoginRequiredAPIView):
    def get(self, request, *args, **kwargs):
        return Response(UserFastSerializer(request.user).data)

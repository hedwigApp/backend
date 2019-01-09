from rest_framework import generics
from rest_framework.views import APIView

from app import permissions


class AnonCreateView(generics.CreateAPIView):
    permission_classes = []


class AnonRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]


class AnonListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]


class LoginRequiredAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]


class AnonymousAPIView(APIView):
    permission_classes = [permissions.AllowAny]

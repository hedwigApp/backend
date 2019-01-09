from rest_framework import serializers

from a12n.models import User


class UserFastSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
        ]

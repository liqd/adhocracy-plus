from rest_framework import serializers

from apps.users.models import User


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('pk', 'username', '_avatar')

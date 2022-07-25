from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', '_avatar', 'is_self')

    def get_is_self(self, instance):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return user == instance
        return False

from rest_framework import serializers

from .models import Choin


class ChoinSerializer(serializers.ModelSerializer):
    meta_info = serializers.SerializerMethodField()

    class Meta:
        model = Choin
        read_only_fields = ("id", "meta_info")

    def get_meta_info(self, obj):
        user = self.context["request"].user
        return obj.get_meta_info(user)

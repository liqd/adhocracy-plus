from rest_framework import serializers

from apps.ideas.serializers import IdeaSerializer

from .models import Choin
from .models import IdeaChoin
from .models import UserIdeaChoin


class ChoinSerializer(serializers.ModelSerializer):
    meta_info = serializers.SerializerMethodField()

    class Meta:
        model = Choin
        read_only_fields = ("id", "meta_info")

    def get_meta_info(self, obj):
        user = self.context["request"].user
        return obj.get_meta_info(user)


class IdeaChoinSerializer(serializers.ModelSerializer):
    idea = IdeaSerializer()
    choins = serializers.FloatField()

    class Meta:
        model = IdeaChoin
        read_only_fields = (
            "id",
            "meta_info",
        )
        fields = "__all__"


class UserIdeaChoinSerializer(serializers.ModelSerializer):
    idea = IdeaSerializer()
    choins = serializers.FloatField()

    class Meta:
        model = UserIdeaChoin
        read_only_fields = (
            "id",
            "meta_info",
        )
        exclude = ("user",)

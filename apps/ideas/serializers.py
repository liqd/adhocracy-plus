from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Idea
        fields = ('name', 'description')

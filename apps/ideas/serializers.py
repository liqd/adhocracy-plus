from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):

    creator = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ('name', 'description', 'creator', 'created')
        read_only_fields = ('creator', 'created')

    def get_creator(self, idea):
        return idea.creator.username

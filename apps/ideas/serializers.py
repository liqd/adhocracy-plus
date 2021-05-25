from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):

    creator = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    positive_rating_count = serializers.SerializerMethodField()
    negative_rating_count = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = ('pk', 'name', 'description', 'creator', 'created',
                  'comment_count', 'positive_rating_count',
                  'negative_rating_count')
        read_only_fields = ('creator', 'created')

    def get_creator(self, idea):
        return idea.creator.username

    def get_comment_count(self, idea):
        return idea.comment_count

    def get_positive_rating_count(self, idea):
        return idea.positive_rating_count

    def get_negative_rating_count(self, idea):
        return idea.negative_rating_count

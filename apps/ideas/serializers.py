from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):

    description = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    positive_rating_count = serializers.SerializerMethodField()
    negative_rating_count = serializers.SerializerMethodField()
    labels = serializers.StringRelatedField(many=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Idea
        fields = ('pk', 'name', 'description', 'creator', 'created',
                  'reference_number', 'image', 'comment_count',
                  'positive_rating_count', 'negative_rating_count',
                  'labels', 'category')
        read_only_fields = ('pk', 'creator', 'created', 'reference_number')

    def get_description(self, idea):
        return strip_tags(idea.description)

    def get_creator(self, idea):
        return idea.creator.username

    def get_comment_count(self, idea):
        return idea.comment_count

    def get_positive_rating_count(self, idea):
        return idea.positive_rating_count

    def get_negative_rating_count(self, idea):
        return idea.negative_rating_count

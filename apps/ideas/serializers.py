from django.utils.html import strip_tags
from rest_framework import serializers

from adhocracy4.categories.models import Category
from adhocracy4.labels.models import Label

from .models import Idea


class LabelListingField(serializers.StringRelatedField):
    def to_internal_value(self, label):
        return Label.objects.get(pk=label)


class DescriptionSerializerField(serializers.Field):

    def to_representation(self, description):
        return strip_tags(description)

    def to_internal_value(self, description):
        return description


class IdeaSerializer(serializers.ModelSerializer):

    description = DescriptionSerializerField()
    creator = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    positive_rating_count = serializers.SerializerMethodField()
    negative_rating_count = serializers.SerializerMethodField()
    labels = LabelListingField(many=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Idea
        fields = ('pk', 'name', 'description', 'creator', 'created',
                  'reference_number', 'image', 'comment_count',
                  'positive_rating_count', 'negative_rating_count',
                  'labels', 'category')
        read_only_fields = ('pk', 'creator', 'created', 'reference_number')

    def get_creator(self, idea):
        return idea.creator.username

    def get_comment_count(self, idea):
        if hasattr(idea, 'comment_count'):
            return idea.comment_count
        else:
            return 0

    def get_positive_rating_count(self, idea):
        if hasattr(idea, 'positive_rating_count'):
            return idea.positive_rating_count
        else:
            return 0

    def get_negative_rating_count(self, idea):
        if hasattr(idea, 'negative_rating_count'):
            return idea.negative_rating_count
        else:
            return 0

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        validated_data['module'] = self.context['view'].module
        if 'category_pk' in self.context['request'].POST:
            category_pk = self.context['request'].POST['category_pk']
            category = Category.objects.get(pk=category_pk)
            validated_data['category'] = category

        return super().create(validated_data)

from rest_framework import serializers

from adhocracy4.categories.models import Category
from adhocracy4.modules.models import Module

from .models import Like
from .models import LiveQuestion


class LiveQuestionSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = LiveQuestion
        exclude = ('module', 'created', 'modified')

    def get_likes(self, livequestion):
        session = self.context['request'].session.session_key
        session_like = bool(
            livequestion.livequestion_likes.filter(session=session).first())
        if hasattr(livequestion, 'like_count'):
            like_count = livequestion.like_count
        else:
            like_count = 0
        result = {
            'count': like_count,
            'session_like': session_like
        }
        return result

    def create(self, validated_data):
        module_pk = self.context['view'].module_pk
        module = Module.objects.get(pk=module_pk)
        category_pk = self.context['view'].kwargs['category']
        if category_pk:
            category = Category.objects.get(pk=category_pk)
            validated_data['category'] = category
        validated_data['module'] = module
        livequestion = super().create(validated_data)

        return livequestion


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ('id',)

    def create(self, validated_data):
        return Like.objects.get_or_create(**validated_data)

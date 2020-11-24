from rest_framework import serializers

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
        result = {
            'count': livequestion.like_count,
            'session_like': session_like
        }
        return result


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ('id',)

    def create(self, validated_data):
        return Like.objects.get_or_create(**validated_data)

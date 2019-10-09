from rest_framework import serializers

from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Question
        exclude = ('module', 'created', 'modified')

    def get_likes(self, question):
        session = self.context['request'].session.session_key
        session_like = bool(
            question.question_likes.filter(session=session).first())
        result = {
            'count': question.like_count,
            'session_like': session_like
        }
        return result

from rest_framework import serializers

from adhocracy4.comments.models import Comment
from adhocracy4.comments_async import serializers as a4_serializers
from apps.contrib.dates import get_date_display
from apps.moderatorfeedback.models import ModeratorCommentFeedback


class ModeratorCommentFeedbackSerializer(serializers.ModelSerializer):
    last_edit = serializers.SerializerMethodField()

    class Meta:
        model = ModeratorCommentFeedback
        fields = ["last_edit", "pk", "feedback_text"]
        read_only_fields = ["last_edit", "pk"]

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        validated_data["comment"] = self.context["view"].comment

        return super().create(validated_data)

    def update(self, feedback, validated_data):
        validated_data["creator"] = self.context["request"].user

        return super().update(feedback, validated_data)

    def get_last_edit(self, feedback):
        if feedback.modified:
            return get_date_display(feedback.modified)
        else:
            return get_date_display(feedback.created)


class CommentWithFeedbackSerializer(a4_serializers.CommentSerializer):
    moderator_feedback = ModeratorCommentFeedbackSerializer(read_only=True)

    class Meta:
        model = Comment
        read_only_fields = a4_serializers.CommentSerializer.Meta.read_only_fields + (
            "moderator_comment_feedback",
        )
        exclude = ("creator",)


class CommentWithFeedbackListSerializer(CommentWithFeedbackSerializer):
    """Serializer for the comments to be used when viewed as list."""


class ThreadSerializer(CommentWithFeedbackSerializer):
    """Serializes a comment including child comment (replies)."""

    child_comments = CommentWithFeedbackSerializer(many=True, read_only=True)


class ThreadListSerializer(CommentWithFeedbackListSerializer):
    """
    Serializes comments when viewed.
    As list including child comment (replies).
    """

    child_comments = CommentWithFeedbackListSerializer(many=True, read_only=True)

from rest_framework import serializers

from adhocracy4 import transforms
from adhocracy4.comments.models import Comment
from adhocracy4.comments_async import serializers as a4_serializers
from apps.contrib.dates import get_date_display
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from apps.moderatorfeedback.models import ModeratorFeedback


class ModeratorFeedbackSerializer(serializers.ModelSerializer):
    last_edit = serializers.SerializerMethodField()

    class Meta:
        model = ModeratorFeedback
        fields = ["last_edit", "pk", "feedback_text"]
        read_only_fields = ["last_edit", "pk"]

    def get_last_edit(self, feedback):
        if feedback is None:
            return None
        if feedback.modified:
            return get_date_display(feedback.modified)
        return get_date_display(feedback.created)


class ModeratorCommentFeedbackSerializer(serializers.ModelSerializer):
    last_edit = serializers.SerializerMethodField()
    mark_resolved = serializers.BooleanField(
        write_only=True, required=False, default=True
    )

    class Meta:
        model = ModeratorCommentFeedback
        fields = ["last_edit", "mark_resolved", "pk", "feedback_text"]
        read_only_fields = ["last_edit", "pk"]

    @staticmethod
    def _mark_comment_read(comment):
        if not comment.is_reviewed:
            comment.is_reviewed = True
            comment.save(ignore_modified=True)

    def create(self, validated_data):
        mark_resolved = validated_data.pop("mark_resolved", True)
        validated_data["creator"] = self.context["request"].user
        comment = self.context["view"].comment
        validated_data["comment"] = comment

        feedback = super().create(validated_data)
        if mark_resolved:
            self._mark_comment_read(comment)
        return feedback

    def update(self, feedback, validated_data):
        mark_resolved = validated_data.pop("mark_resolved", True)
        validated_data["creator"] = self.context["request"].user

        feedback = super().update(feedback, validated_data)
        if mark_resolved:
            self._mark_comment_read(feedback.comment)
        return feedback

    def get_last_edit(self, feedback):
        if feedback is None:
            return None
        if feedback.modified:
            return get_date_display(feedback.modified)
        return get_date_display(feedback.created)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["feedback_text"] = transforms.clean_html_field(
            instance.feedback_text or ""
        )
        return data


class CommentWithFeedbackSerializer(a4_serializers.CommentSerializer):
    moderator_feedback = ModeratorCommentFeedbackSerializer(read_only=True)

    class Meta:
        model = Comment
        read_only_fields = a4_serializers.CommentSerializer.Meta.read_only_fields + (
            "moderator_feedback",
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

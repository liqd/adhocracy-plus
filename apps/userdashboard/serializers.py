from django.urls import reverse
from django.utils.translation import gettext as _
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from adhocracy4.comments.models import Comment
from apps.contrib.dates import get_date_display
from apps.moderatorfeedback.serializers import ModeratorCommentFeedbackSerializer


class ModerationCommentSerializer(serializers.ModelSerializer):
    comment_url = serializers.SerializerMethodField()
    is_unread = serializers.SerializerMethodField()
    is_modified = serializers.SerializerMethodField()
    last_edit = serializers.SerializerMethodField()
    moderator_feedback = ModeratorCommentFeedbackSerializer(read_only=True)
    num_reports = serializers.SerializerMethodField()
    feedback_api_url = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    user_profile_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "comment",
            "comment_url",
            "feedback_api_url",
            "is_unread",
            "is_blocked",
            "is_moderator_marked",
            "is_modified",
            "last_edit",
            "moderator_feedback",
            "num_reports",
            "pk",
            "user_image",
            "user_name",
            "user_profile_url",
        ]

    def get_comment_url(self, instance):
        return instance.get_absolute_url()

    def get_is_modified(self, comment):
        return comment.modified is not None

    def get_last_edit(self, comment):
        if comment.modified:
            return get_date_display(comment.modified)
        else:
            return get_date_display(comment.created)

    def get_feedback_api_url(self, comment):
        return reverse("moderatorfeedback-list", kwargs={"comment_pk": comment.pk})

    def get_num_reports(self, comment):
        return comment.num_reports

    def get_user_name(self, comment):
        if comment.is_censored or comment.is_removed:
            return _("unknown user")
        return str(comment.creator.username)

    def get_user_image_fallback(self, comment):
        """Load small thumbnail images for default user images."""
        if comment.is_censored or comment.is_removed:
            return None
        try:
            if comment.creator.avatar_fallback:
                return comment.creator.avatar_fallback
        except AttributeError:
            pass
        return None

    def get_user_image(self, comment):
        """Load small thumbnail images for user images."""
        if comment.is_censored or comment.is_removed:
            return None
        try:
            if comment.creator.avatar:
                avatar = get_thumbnailer(comment.creator.avatar)["avatar"]
                return avatar.url
        except AttributeError:
            pass
        return self.get_user_image_fallback(comment)

    def get_user_profile_url(self, comment):
        if comment.is_censored or comment.is_removed:
            return ""
        try:
            return comment.creator.get_absolute_url()
        except AttributeError:
            return ""

    def get_is_unread(self, comment):
        return not comment.is_reviewed

    def update(self, instance, validated_data):
        """Update comment instance without changing comment.modified.

        This is essentially copied from
        rest_framework.serializers.ModelSerializer.update(),
        only difference is ignore_modified=true when saving the instance.
        See also here:
        https://github.com/encode/django-rest-framework/blob/master/rest_framework/serializers.py#L991-L1015
        """
        raise_errors_on_nested_writes("update", self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save(ignore_modified=True)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

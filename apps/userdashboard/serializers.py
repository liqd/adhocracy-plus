from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from adhocracy4.comments.models import Comment
from apps.contrib.dates import get_date_display
from apps.contrib.templatetags.item_tags import get_item_url
from apps.ideas.models import Idea
from apps.moderatorfeedback.serializers import ModeratorCommentFeedbackSerializer


def _is_hidden(instance):
    return getattr(instance, "is_censored", False) or getattr(
        instance, "is_removed", False
    )


def get_creator_name(instance):
    if _is_hidden(instance):
        return _("unknown user")
    return str(instance.creator.username)


def get_creator_image(instance):
    if _is_hidden(instance):
        return None
    creator = instance.creator
    try:
        if creator.avatar:
            return get_thumbnailer(creator.avatar)["avatar"].url
    except AttributeError:
        pass
    try:
        if creator.avatar_fallback:
            return creator.avatar_fallback
    except AttributeError:
        pass
    return None


def get_creator_profile_url(instance):
    if _is_hidden(instance):
        return ""
    try:
        return instance.creator.get_absolute_url()
    except AttributeError:
        return ""


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
        return get_creator_name(comment)

    def get_user_image(self, comment):
        return get_creator_image(comment)

    def get_user_profile_url(self, comment):
        return get_creator_profile_url(comment)

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


class ModerationItemMixin(serializers.Serializer):
    """Shared fields for comments and ideas in the moderation list."""

    item_type = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    moderate_url = serializers.SerializerMethodField()
    api_url = serializers.SerializerMethodField()


class ModerationCommentItemSerializer(ModerationItemMixin, ModerationCommentSerializer):
    class Meta(ModerationCommentSerializer.Meta):
        fields = ModerationCommentSerializer.Meta.fields + [
            "item_type",
            "label",
            "text",
            "title",
            "url",
            "moderate_url",
            "api_url",
        ]

    def get_item_type(self, comment):
        return "comment"

    def get_label(self, comment):
        return _("Comment")

    def get_text(self, comment):
        return comment.comment

    def get_title(self, comment):
        return None

    def get_url(self, comment):
        return comment.get_absolute_url()

    def get_moderate_url(self, comment):
        return ""

    def get_api_url(self, comment):
        return reverse(
            "moderationcomments-detail",
            kwargs={"project_pk": comment.project_id, "pk": comment.pk},
        )


class ModerationIdeaSerializer(ModerationItemMixin, serializers.ModelSerializer):
    last_edit = serializers.SerializerMethodField()
    is_modified = serializers.SerializerMethodField()
    is_unread = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    is_moderator_marked = serializers.SerializerMethodField()
    num_reports = serializers.SerializerMethodField()
    moderator_feedback = serializers.SerializerMethodField()
    feedback_api_url = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    user_profile_url = serializers.SerializerMethodField()

    class Meta:
        model = Idea
        fields = [
            "pk",
            "item_type",
            "label",
            "text",
            "title",
            "url",
            "moderate_url",
            "api_url",
            "last_edit",
            "is_modified",
            "is_unread",
            "is_blocked",
            "is_moderator_marked",
            "num_reports",
            "moderator_feedback",
            "feedback_api_url",
            "user_name",
            "user_image",
            "user_profile_url",
        ]

    def get_item_type(self, idea):
        return "idea"

    def get_label(self, idea):
        return _("Idea")

    def get_text(self, idea):
        return strip_tags(idea.description)

    def get_title(self, idea):
        return idea.name

    def get_url(self, idea):
        return idea.get_absolute_url()

    def get_moderate_url(self, idea):
        return get_item_url(idea, "moderate", raises=False)

    def get_api_url(self, idea):
        return ""

    def get_last_edit(self, idea):
        if idea.modified:
            return get_date_display(idea.modified)
        return get_date_display(idea.created)

    def get_is_modified(self, idea):
        return idea.modified is not None

    def get_is_unread(self, idea):
        return False

    def get_is_blocked(self, idea):
        return False

    def get_is_moderator_marked(self, idea):
        return False

    def get_num_reports(self, idea):
        return 0

    def get_moderator_feedback(self, idea):
        return None

    def get_feedback_api_url(self, idea):
        return ""

    def get_user_name(self, idea):
        return get_creator_name(idea)

    def get_user_image(self, idea):
        return get_creator_image(idea)

    def get_user_profile_url(self, idea):
        return get_creator_profile_url(idea)


class ModerationItemSerializer(serializers.BaseSerializer):
    """Serializes comments and ideas with a shared set of fields."""

    def to_representation(self, instance):
        if isinstance(instance, Comment):
            serializer = ModerationCommentItemSerializer(instance, context=self.context)
        else:
            serializer = ModerationIdeaSerializer(instance, context=self.context)
        return serializer.data

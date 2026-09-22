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


class ModerationItemMixin(serializers.Serializer):
    """Shared representation of comments and ideas in the moderation list."""

    item_type = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    moderate_url = serializers.SerializerMethodField()
    api_url = serializers.SerializerMethodField()

    def get_item_type(self, instance):
        return self.item_type_value

    def get_label(self, instance):
        return self.label_value

    def get_text(self, instance):
        return self.text_value(instance)

    def get_title(self, instance):
        return self.title_value(instance)

    def get_url(self, instance):
        return self.get_absolute_url_value(instance)

    def get_moderate_url(self, instance):
        return self.moderate_url_value(instance)

    def get_api_url(self, instance):
        return self.api_url_value(instance)


class ModerationCommentItemSerializer(ModerationItemMixin, ModerationCommentSerializer):
    item_type_value = "comment"
    label_value = _("Comment")

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

    def text_value(self, comment):
        return comment.comment

    def title_value(self, comment):
        return None

    def get_absolute_url_value(self, comment):
        return comment.get_absolute_url()

    def moderate_url_value(self, comment):
        return ""

    def api_url_value(self, comment):
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

    item_type_value = "idea"
    label_value = _("Idea")

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

    def text_value(self, idea):
        return strip_tags(idea.description)

    def title_value(self, idea):
        return idea.name

    def get_absolute_url_value(self, idea):
        return idea.get_absolute_url()

    def moderate_url_value(self, idea):
        return get_item_url(idea, "moderate", raises=False)

    def api_url_value(self, idea):
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
        return str(idea.creator.username)

    def get_user_image(self, idea):
        try:
            if idea.creator.avatar:
                avatar = get_thumbnailer(idea.creator.avatar)["avatar"]
                return avatar.url
        except AttributeError:
            pass
        try:
            if idea.creator.avatar_fallback:
                return idea.creator.avatar_fallback
        except AttributeError:
            pass
        return None

    def get_user_profile_url(self, idea):
        try:
            return idea.creator.get_absolute_url()
        except AttributeError:
            return ""


class ModerationItemSerializer(serializers.BaseSerializer):
    """Serializes comments and ideas with a shared set of fields."""

    def to_representation(self, instance):
        if isinstance(instance, Comment):
            serializer = ModerationCommentItemSerializer(instance, context=self.context)
        else:
            serializer = ModerationIdeaSerializer(instance, context=self.context)
        return serializer.data

from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from adhocracy4.comments.models import Comment
from apps.classifications.models import AIClassification
from apps.classifications.models import UserClassification


class CommentSerializer(serializers.ModelSerializer):

    comment_url = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['comment_url', 'user_name', 'user_image']

    def get_comment_url(self, instance):
        return instance.get_absolute_url()

    def get_user_name(self, instance):
        if instance.is_censored or instance.is_removed:
            return _('unknown user')
        return str(instance.creator.username)

    def get_user_image_fallback(self, obj):
        """Load small thumbnail images for default user images."""
        if(obj.is_censored or obj.is_removed):
            return None
        try:
            if obj.creator.avatar_fallback:
                return obj.creator.avatar_fallback
        except AttributeError:
            pass
        return None

    def get_user_image(self, obj):
        """Load small thumbnail images for user images."""
        if(obj.is_censored or obj.is_removed):
            return None
        try:
            if obj.creator.avatar:
                avatar = get_thumbnailer(obj.creator.avatar)['avatar']
                return avatar.url
        except AttributeError:
            pass
        return self.get_user_image_fallback(obj)


class UserClassificationSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)
    classification = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = UserClassification
        fields = ['comment', 'classification', 'comment_text',
                  'user_message', 'created']

    def get_classification(self, instance):
        return instance.get_classification_display()

    def get_created(self, instance):
        return instance.created.strftime('%d.%m.%y')


class AIClassificationSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)
    classification = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = AIClassification
        fields = ['comment', 'classification', 'comment_text', 'created']

    def get_classification(self, instance):
        return instance.get_classification_display()

    def get_created(self, instance):
        return instance.created.strftime('%d.%m.%y')

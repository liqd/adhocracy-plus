from rest_framework import serializers

from apps.users.models import User


class AccountSerializer(serializers.ModelSerializer):

    user_image = serializers.ImageField(source="_avatar", required=False)
    user_image_fallback = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("pk", "username", "user_image", "user_image_fallback", "language")

    def get_user_image_fallback(self, user):
        """Serve fallback as png as used in app."""
        try:
            if user.avatar_fallback_png:
                url = user.avatar_fallback_png
                request = self.context.get("request", None)
                if request is not None:
                    return request.build_absolute_uri(url)
                return url
        except AttributeError:
            pass
        return None

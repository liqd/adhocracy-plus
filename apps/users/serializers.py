from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_self = serializers.SerializerMethodField()
    user_image = serializers.ImageField(source="_avatar")
    user_image_fallback = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "user_image", "user_image_fallback", "is_self")

    def get_is_self(self, instance):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return user == instance
        return False

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

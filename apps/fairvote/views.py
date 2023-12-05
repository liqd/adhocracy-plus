from django.contrib.auth import get_user_model

from .models import Choin
from .models import Idea
from .models import IdeaChoin

USER_MODEL = get_user_model()


class ChoinView:
    @staticmethod
    def create_ideas_choins():
        for idea in Idea.objects.all():
            idea_obj, created = IdeaChoin.objects.update_or_create(idea=idea)

    @staticmethod
    def create_users_choins():
        for user in USER_MODEL.objects.all():
            user_obj, created = Choin.objects.update_or_create(user=user)

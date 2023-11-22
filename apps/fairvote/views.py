from django.contrib.auth import get_user_model
from django.db.models import F

from .models import Choin
from .models import Idea
from .models import IdeaChoin

USER_MODEL = get_user_model()


class ChoinView:
    @staticmethod
    def order_by_supporting(module):
        ideas_choins = IdeaChoin.objects.filter(idea__module=module)
        sorted_ideas_choins = sorted(
            ideas_choins, key=lambda x: x.get_remaining_choins()
        )
        return sorted_ideas_choins

    @staticmethod
    def increase_choins_to_accept_idea(module):
        most_supported_idea = ChoinView.order_by_supporting(module)[0]
        remaining_choins = most_supported_idea.get_remaining_choins()
        supporters = most_supported_idea.get_supporters()
        choins_per_user = remaining_choins / supporters.count()
        Choin.objects.filter(user__in=supporters.values("user").distinct()).update(
            choins=F("choins") + choins_per_user
        )

    @staticmethod
    def create_ideas_choins():
        for idea in Idea.objects.all():
            idea_obj, created = IdeaChoin.objects.update_or_create(idea=idea)

    @staticmethod
    def create_users_choins():
        for user in USER_MODEL.objects.all():
            user_obj, created = Choin.objects.update_or_create(user=user)

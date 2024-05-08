from django.contrib.auth import get_user_model
from django.views.generic import ListView

from .algorithms import fair_acceptance_order
from .algorithms import get_supporters
from .models import Choin
from .models import ChoinEvent
from .models import Idea
from .models import IdeaChoin
from .models import ProjectChoin
from .models import UserIdeaChoin

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


class ChoinEventListView(ListView):
    model = ChoinEvent
    template_name = "a4_candy_fairvote/choinevent_list.html"  # Update with your actual template path
    context_object_name = "choinevent_list"

    def get_queryset(self):
        import json

        if self.request.user.is_anonymous:
            return ChoinEvent.objects.none()
        choinevents = ChoinEvent.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )
        for event in choinevents:
            if event.content_params:
                parsed_content_params = json.loads(event.content_params)
                for key, val in parsed_content_params.items():
                    event.__setattr__(key, val)
        try:
            user_choin = Choin.objects.get(user=self.request.user)
            choinevents.user_paid = user_choin.supported_ideas_paid
            choinevents.paid = ProjectChoin.objects.get(
                project=user_choin.module.project
            ).paid

        except Choin.DoesNotExist:
            choinevents.user_paid = "unavailable"
            choinevents.paid = "unavailable"
        return choinevents


def accepted_ideas(request, organisation_slug, obj_id):
    from django.shortcuts import render

    request_user = request.user

    if request_user.is_authenticated:
        authenticated_as = request_user.username
    else:
        authenticated_as = None

    modules = {}
    user_fairvote_modules = Choin.objects.filter(
        user=request_user.pk, module__project__pk=obj_id, module__blueprint_type="FV"
    )

    for fv_choin in user_fairvote_modules:
        fv_module = fv_choin.module
        modules[fv_module.pk] = {
            "name": fv_module.name,
            "choins": fv_choin.choins,
            "ideas": [],
        }
        ideas = Idea.objects.filter(module=fv_module, moderator_status="ACCEPTED")

        for idea in ideas:
            user_idea_choins = UserIdeaChoin.objects.filter(
                user=request_user.pk, idea=idea
            ).first()
            idea_choin = IdeaChoin.objects.get(idea=idea)
            supporters_count = get_supporters(idea).count()
            idea_url = idea.get_absolute_url()
            modules[fv_module.pk]["ideas"].append(
                {
                    "id": idea.pk,
                    "name": idea.name,
                    "url": idea_url,
                    "creator": idea.creator.username,
                    "choins": idea_choin.choins,
                    "supporters_count": supporters_count,
                    "goal": idea_choin.goal,
                    "support": user_idea_choins.choins if user_idea_choins else 0,
                }
            )

    context = {
        "authenticated_as": authenticated_as,
        "user_fairvote_modules": modules if (modules or modules != {}) else None,
        "is_read_only": False,
        "style": "ideas",
    }
    return render(request, "a4_candy_fairvote/accepted_idea_list.html", context)


def ideas_fair_acceptance_order(request, organisation_slug, obj_id):
    from django.shortcuts import render

    top = int(request.GET.get("top", 5))
    user = request.user
    ideas = fair_acceptance_order(obj_id, user, top)
    context = {
        "ideas": ideas,
        "is_read_only": False,
        "style": "ideas",
    }
    return render(
        request, "a4_candy_fairvote/ideas_fair_acceptance_order.html", context
    )

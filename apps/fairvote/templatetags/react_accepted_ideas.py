from django import template
from django.template.loader import render_to_string

from apps.fairvote.algorithms import get_supporters
from apps.fairvote.models import Choin
from apps.fairvote.models import ChoinEvent
from apps.fairvote.models import Idea
from apps.fairvote.models import IdeaChoin
from apps.fairvote.models import UserIdeaChoin

register = template.Library()


@register.simple_tag(takes_context=True)
def react_accepted_ideas(context, obj_id):
    request = context["request"]
    user = request.user
    # contenttype = ContentType.objects.get_for_model(obj)
    # permission = "{ct.app_label}.invest_{ct.model}".format(ct=contenttype)
    # has_rate_permission = user.has_perm(permission, obj)

    # would_have_rate_permission = NormalUser().would_have_perm(permission, obj)

    if user.is_authenticated:
        authenticated_as = user.username
    else:
        authenticated_as = None

    modules = {}
    user_fairvote_modules = Choin.objects.filter(
        user=user.pk, module__project__pk=obj_id, module__blueprint_type="FV"
    )

    for fv_choin in user_fairvote_modules:
        fv_module = fv_choin.module
        joined_module = (
            ChoinEvent.objects.filter(user=user, module=fv_module)
            .order_by("created_at")
            .first()
            .created_at
        )
        ideas = Idea.objects.filter(
            module=fv_module,
            moderator_status="ACCEPTED",
            moderator_feedback_text__modified__lt=joined_module,
        ).order_by("-moderator_feedback_text__modified")
        if ideas:
            modules[fv_module.pk] = {
                "name": fv_module.name,
                "choins": fv_choin.choins,
                "ideas": [],
                "joined": joined_module,
            }

        for idea in ideas:
            user_idea_choins = UserIdeaChoin.objects.filter(
                user=user.pk, idea=idea
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
                    "accepted_at": idea.moderator_feedback_text.modified,
                }
            )

    context = {
        "authenticated_as": authenticated_as,
        "user_fairvote_modules": modules if (modules or modules != {}) else None,
        "is_read_only": False,
        "style": "ideas",
    }
    print(context)
    return render_to_string("a4_candy_fairvote/accepted_ideas_events.html", context)

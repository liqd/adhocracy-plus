import json

from django import template
from django.utils.html import format_html

from apps.fairvote.models import Choin
from apps.fairvote.models import Idea
from apps.fairvote.models import IdeaChoin
from apps.fairvote.models import UserIdeaChoin

register = template.Library()


@register.simple_tag(takes_context=True)
def react_user_idea_choins(context, obj):
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
        user=user.pk, module__project=obj.pk, module__blueprint_type="FV"
    )
    print("user ideas: ", user_fairvote_modules)
    for fv_choin in user_fairvote_modules:
        fv_module = fv_choin.module
        modules[fv_module.pk] = {
            "name": fv_module.name,
            "choins": fv_choin.choins,
            "ideas": [],
        }
        ideas = Idea.objects.filter(module=fv_module, moderator_status="ACCEPTED")
        for idea in ideas:
            user_idea_choins = UserIdeaChoin.objects.filter(user=user.pk, idea=idea)
            idea_choin = IdeaChoin.objects.get(idea=idea)
            supporters_count = idea_choin.get_supporters().count()
            print(idea.ratings)
            idea_url = idea.get_absolute_url()
            modules[fv_module.pk]["ideas"].append(
                {
                    "id": idea.pk,
                    "name": idea.name,
                    "url": idea_url,
                    "choins": idea.choins,
                    "supporters_count": supporters_count,
                    "goal": idea_choin.goal,
                    "support": user_idea_choins.choins if user_idea_choins else 0,
                }
            )

    attributes = {
        "objectId": obj.pk,
        "authenticatedAs": authenticated_as,
        "userFairvoteModules": modules if (modules or modules != {}) else None,
        "isReadOnly": False,
        "style": "ideas",
    }

    return format_html(
        '<div data-aplus-widget="fv_modules" data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes),
    )

import json

from django import template
from django.utils.html import format_html

from apps.fairvote.algorithms import get_supporters
from apps.fairvote.models import Choin
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
    # should check whether module has buy attribute
    user_fairvote_modules = Choin.objects.filter(
        user=user.pk, module__project=obj.pk, module__blueprint_type="FV"
    )
    for fv_choin in user_fairvote_modules:
        fv_module = fv_choin.module
        modules[fv_module.pk] = {
            "name": fv_module.name,
            "choins": fv_choin.choins,
            "ideas": [],
        }
        user_idea_choins = UserIdeaChoin.objects.filter(
            user=user.pk,
            idea__module=fv_choin.module,
            idea__moderator_status="ACCEPTED",
        )
        if user_idea_choins:
            for user_idea in user_idea_choins:
                content_idea = user_idea.idea
                idea_choin = IdeaChoin.objects.get(idea=content_idea)
                supporters_count = get_supporters(content_idea).count() - 1
                idea_url = content_idea.get_absolute_url()
                modules[fv_module.pk]["ideas"].append(
                    {
                        "id": content_idea.pk,
                        "name": content_idea.name,
                        "url": idea_url,
                        "choins": user_idea.choins,
                        "supporters_count": supporters_count,
                        "goal": idea_choin.goal,
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

import json

from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.html import format_html

from adhocracy4.rules.discovery import NormalUser
from apps.fairvote.models import Choin
from apps.fairvote.models import Idea
from apps.fairvote.models import UserIdeaChoin

register = template.Library()


@register.simple_tag(takes_context=True)
def react_choins(context, obj):
    request = context["request"]
    user = request.user
    idea_obj = Idea.objects.filter(module=obj).first()
    if not idea_obj:
        return render_to_string(
            "a4_candy_fairvote/user_choins.html", {"user_choins_value": 0}
        )
    contenttype = ContentType.objects.get_for_model(idea_obj)
    permission = "{ct.app_label}.rate_{ct.model}".format(ct=contenttype)

    has_rate_permission = user.has_perm(permission, idea_obj)
    would_have_rate_permission = NormalUser().would_have_perm(permission, idea_obj)
    print(has_rate_permission, would_have_rate_permission)
    if user.is_authenticated and (has_rate_permission or would_have_rate_permission):
        user_choins = Choin.objects.filter(module=obj, user=user.pk).first()
        user_choins_value = user_choins.choins if user_choins else 0
        return render_to_string(
            "a4_candy_fairvote/user_choins.html",
            {"user_choins_value": user_choins_value},
        )
    else:
        return render_to_string(
            "a4_candy_fairvote/user_choins.html", {"user_choins_value": None}
        )


@register.simple_tag(takes_context=True)
def react_invested_choins(context, obj):
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
    user_idea_choins = UserIdeaChoin.objects.filter(
        user=user.pk, idea=obj.pk, idea__moderator_status="ACCEPTED"
    ).first()
    if user_idea_choins is not None:
        user_choins_value = user_idea_choins.choins
        user_choins_id = user_idea_choins.pk
    else:
        user_choins_value = None
        user_choins_id = -1

    attributes = {
        "objectId": obj.pk,
        "authenticatedAs": authenticated_as,
        "userChoins": user_choins_value,
        "userChoinsId": user_choins_id,
        "isReadOnly": False,
        "style": "ideas",
    }

    return format_html(
        '<div data-aplus-widget="invested_choins" data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes),
    )

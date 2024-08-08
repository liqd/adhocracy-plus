import json

from django import template
from django.template.loader import render_to_string

from apps.fairvote.models import Choin
from apps.fairvote.models import ChoinEvent
from apps.fairvote.models import ProjectChoin

register = template.Library()


@register.simple_tag(takes_context=True)
def react_choin_events(context, obj=None):
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
    choinevents = ChoinEvent.objects.none()
    if not user.is_anonymous:
        choinevents = ChoinEvent.objects.filter(user=user).order_by("-created_at")
        for event in choinevents:
            if event.content_params:
                parsed_content_params = json.loads(event.content_params)
                for key, val in parsed_content_params.items():
                    event.__setattr__(key, val)
        try:
            user_choin = Choin.objects.get(user=user)
            choinevents.user_paid = user_choin.supported_ideas_paid
            project_choin = ProjectChoin.objects.get(project=user_choin.module.project)
            choinevents.paid = project_choin.paid
            choinevents.project = project_choin.project

        except Choin.DoesNotExist:
            choinevents.user_paid = "unavailable"
            choinevents.paid = "unavailable"
        except ProjectChoin.DoesNotExist:
            choinevents.user_paid = 0
            choinevents.paid = 0
    context = {
        "authenticated_as": authenticated_as,
        "choinevent_list": choinevents,
        "is_read_only": False,
        "style": "ideas",
    }
    print(context)
    return render_to_string("a4_candy_fairvote/choinevent_list.html", context)

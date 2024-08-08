from django import template
from django.template.loader import render_to_string

from apps.fairvote.models import MAX_ACCEPTED_IDEAS
from apps.fairvote.models import Idea

register = template.Library()


@register.simple_tag(takes_context=True)
def react_user_vote_count(context, obj):
    request = context["request"]
    user = request.user
    # contenttype = ContentType.objects.get_for_model(obj)
    # permission = "{ct.app_label}.invest_{ct.model}".format(ct=contenttype)
    # has_rate_permission = user.has_perm(permission, obj)

    # would_have_rate_permission = NormalUser().would_have_perm(permission, obj)

    if user.is_authenticated:
        ideas = (
            Idea.objects.filter(module=obj, choin__order__lt=MAX_ACCEPTED_IDEAS)
            .order_by("choin__order")
            .filter(ratings__creator=user, ratings__value=1)
        )
        vote_count = ideas.count() if ideas else 0
        print("vote count: ", vote_count)
        return render_to_string(
            "a4_candy_fairvote/user_vote_count.html", {"vote_count": vote_count}
        )
    else:
        return render_to_string(
            "a4_candy_fairvote/user_vote_count.html", {"vote_count": None}
        )

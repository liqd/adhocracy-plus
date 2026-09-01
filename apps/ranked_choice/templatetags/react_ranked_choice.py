import json

from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def react_ranked_choice(context):
    module = context.get("module")
    ideas = context.get("ideas") or []
    my_ballot = context.get("my_ballot") or []
    user_can_rank = context.get("user_can_rank") or False
    results_visible = bool(context.get("results_visible"))
    winners = context.get("winners") or []
    results = [
        {"place": winner["place"], "pk": winner["idea"].pk, "name": winner["idea"].name}
        for winner in winners
    ]
    request = context.get("request")
    user_authenticated = bool(
        request and request.user and request.user.is_authenticated
    )

    attributes = {
        "moduleId": module.id,
        "ideas": [{"pk": idea.pk, "name": idea.name} for idea in ideas],
        "myBallot": list(my_ballot),
        "userCanRank": user_can_rank,
        "userAuthenticated": user_authenticated,
        "resultsVisible": results_visible,
        "results": results,
    }

    return format_html(
        '<div data-a4-widget="ranked_choice" data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes),
    )
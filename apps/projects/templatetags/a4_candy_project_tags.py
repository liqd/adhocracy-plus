import json

from django import template
from django.utils.translation import gettext as _
from easy_thumbnails.files import get_thumbnailer

from adhocracy4.comments.models import Comment
from adhocracy4.follows.models import Follow
from adhocracy4.polls.models import Vote
from apps.budgeting.models import Proposal as budget_proposal
from apps.ideas.models import Idea
from apps.interactiveevents.models import Like
from apps.interactiveevents.models import LiveQuestion
from apps.mapideas.models import MapIdea

register = template.Library()


@register.filter
def project_url(project):
    return project.get_absolute_url()


@register.simple_tag
def to_class_name(value):
    return value.__class__.__name__


@register.simple_tag
def get_num_entries(module):
    """Count all user-generated items."""
    item_count = (
        Idea.objects.filter(module=module).count()
        + MapIdea.objects.filter(module=module).count()
        + budget_proposal.objects.filter(module=module).count()
        + Comment.objects.filter(idea__module=module).count()
        + Comment.objects.filter(mapidea__module=module).count()
        + Comment.objects.filter(budget_proposal__module=module).count()
        + Comment.objects.filter(paragraph__chapter__module=module).count()
        + Comment.objects.filter(chapter__module=module).count()
        + Comment.objects.filter(poll__module=module).count()
        + Comment.objects.filter(topic__module=module).count()
        + Comment.objects.filter(subject__module=module).count()
        + Vote.objects.filter(choice__question__poll__module=module).count()
        + LiveQuestion.objects.filter(module=module).count()
        + Like.objects.filter(livequestion__module=module).count()
    )

    return item_count


@register.simple_tag
def project_participation_status(project):
    """Return label and BEM modifier for project participation status."""
    phases = project.published_phases
    if phases.active_phases().exists():
        return {"label": _("running"), "modifier": "running"}
    if phases.future_phases().exists():
        return {"label": _("upcoming"), "modifier": "upcoming"}
    if project.has_finished:
        return {"label": _("completed"), "modifier": "completed"}
    return {"label": _("running"), "modifier": "running"}


@register.simple_tag
def get_project_follower_count(project):
    return Follow.objects.filter(project=project, enabled=True).count()


@register.simple_tag
def get_project_followers(project, limit=4):
    return [
        follow.creator
        for follow in Follow.objects.filter(project=project, enabled=True)
        .select_related("creator")
        .order_by("-created")[:limit]
    ]


def _follower_avatar_data(user):
    avatar_url = ""
    if user.avatar:
        avatar_url = get_thumbnailer(user.avatar)["avatar"].url
    return {
        "pk": user.pk,
        "avatar": avatar_url,
        "avatarFallback": user.avatar_fallback,
    }


@register.simple_tag(takes_context=True)
def project_detail_follow_widget_attrs(context, project):
    """JSON attributes for the project detail follow React widget."""
    request = context["request"]
    follower_users = [
        follow.creator
        for follow in Follow.objects.filter(project=project, enabled=True)
        .select_related("creator")
        .order_by("-created")[:4]
    ]

    # Portal element ids are fixed in project_detail_intro/sidebar templates;
    # see apps/projects/assets/js/project_detail_follow.jsx.
    attrs = {
        "project": project.slug,
        "initialFollowers": [_follower_avatar_data(u) for u in follower_users],
        "initialFollowerCount": Follow.objects.filter(
            project=project, enabled=True
        ).count(),
    }

    if request.user.is_authenticated:
        attrs["authenticatedAs"] = request.user.username
        attrs["user"] = _follower_avatar_data(request.user)

    return json.dumps(attrs)

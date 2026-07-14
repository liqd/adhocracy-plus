import json

from django import template
from django.utils.translation import gettext as _
from easy_thumbnails.files import get_thumbnailer
from guest_user.functions import get_guest_model
from guest_user.functions import is_guest_user

from adhocracy4.comments.models import Comment
from adhocracy4.follows.models import Follow
from adhocracy4.polls.models import Vote
from apps.budgeting.models import Proposal as budget_proposal
from apps.ideas.models import Idea
from apps.interactiveevents.models import Like
from apps.interactiveevents.models import LiveQuestion
from apps.mapideas.models import MapIdea
from apps.projects.timeline import module_cta_label as get_module_cta_label
from apps.projects.timeline import module_date_range as get_module_date_range
from apps.projects.timeline import (
    module_participation_status as get_module_participation_status,
)
from apps.projects.timeline import (
    offline_event_cta_label as get_offline_event_cta_label,
)
from apps.projects.timeline import (
    offline_event_date_label as get_offline_event_date_label,
)
from apps.projects.timeline import (
    offline_event_participation_status as get_offline_event_participation_status,
)
from apps.projects.utils import project_has_result_content

register = template.Library()


def _registered_project_follows(project):
    """Return enabled project follows from registered users only."""
    guest_user_ids = get_guest_model().objects.values_list("user_id", flat=True)
    return Follow.objects.filter(project=project, enabled=True).exclude(
        creator_id__in=guest_user_ids
    )


@register.filter
def has_result_content(project):
    return project_has_result_content(project)


@register.filter
def project_url(project):
    return project.get_absolute_url()


@register.simple_tag
def to_class_name(value):
    return value.__class__.__name__


@register.simple_tag
def get_num_entries(module):
    """Count all user-generated items."""
    return (
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


@register.simple_tag
def participation_timeline_status_tag(module):
    """Return label and BEM modifier for a module on the participation timeline."""
    status, label = get_module_participation_status(module)
    return {"label": label, "modifier": status}


@register.simple_tag
def module_date_range(module):
    return get_module_date_range(module)


@register.simple_tag
def module_cta_label(module):
    return get_module_cta_label(module)


@register.simple_tag
def participation_timeline_offline_event_status_tag(offline_event):
    """Return label and BEM modifier for an offline event on the participation timeline."""
    status, label = get_offline_event_participation_status(offline_event)
    return {"label": label, "modifier": status}


@register.simple_tag
def offline_event_date_label(offline_event):
    return get_offline_event_date_label(offline_event)


@register.simple_tag
def offline_event_cta_label(offline_event):
    return get_offline_event_cta_label(offline_event)


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
    return _registered_project_follows(project).count()


@register.simple_tag
def get_project_followers(project, limit=4):
    return [
        follow.creator
        for follow in _registered_project_follows(project)
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
    registered_follows = _registered_project_follows(project)
    follower_users = [
        follow.creator
        for follow in registered_follows.select_related("creator").order_by("-created")[
            :4
        ]
    ]

    # Portal element ids are fixed in project_detail_intro/sidebar templates;
    # see apps/projects/assets/js/project_detail_follow.jsx.
    attrs = {
        "project": project.slug,
        "initialFollowers": [_follower_avatar_data(u) for u in follower_users],
        "initialFollowerCount": registered_follows.count(),
    }

    if request.user.is_authenticated and not is_guest_user(request.user):
        attrs["authenticatedAs"] = request.user.username
        attrs["user"] = _follower_avatar_data(request.user)

    return json.dumps(attrs)

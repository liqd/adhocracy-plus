import json

from django import template
from django.utils.translation import gettext as _
from easy_thumbnails.files import get_thumbnailer

from adhocracy4.follows.models import Follow
from apps.projects.timeline import module_cta_label as get_module_cta_label
from apps.projects.timeline import module_date_range as get_module_date_range
from apps.projects.timeline import (
    module_participation_status as get_module_participation_status,
)
from apps.projects.utils import count_module_entries
from apps.projects.utils import project_has_result_content

register = template.Library()


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
    return count_module_entries(module)


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

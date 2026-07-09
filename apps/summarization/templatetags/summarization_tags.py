from django import template

from adhocracy4.polls.models import Poll
from apps.debate.models import Subject
from apps.documents.models import Chapter
from apps.ideas.models import Idea
from apps.projects.insights import compute_insight_counts
from apps.topicprio.models import Topic

register = template.Library()


@register.filter
def get_module_by_id(queryset, id):
    """Get a module by ID from a queryset, return None if id is None or invalid."""
    if not id:
        return None
    try:
        return queryset.filter(id=id).first()
    except (ValueError, TypeError):
        return None


def _is_django_model_instance(obj):
    """Return True if obj is a Django model instance (has _meta)."""
    return obj is not None and hasattr(obj, "_meta")


@register.simple_tag
def get_project_stats(project):
    """
    Return statistics for a project.

    Usage: {% get_project_stats project as stats %}

    If project is not a Django model instance (e.g. a mock from summarization test),
    returns empty stats to avoid ORM errors.
    """
    if not _is_django_model_instance(project):
        return {
            "participants": 0,
            "comments": 0,
            "ratings": 0,
            "ideas": 0,
            "contributions": 0,
            "modules": 0,
        }

    insight_counts = compute_insight_counts(project)

    return {
        **insight_counts,
        "contributions": _count_contributions(project),
        "modules": _count_modules(project),
    }


def _count_contributions(project):
    """Count total contributions in a project."""
    return (
        Idea.objects.filter(module__project=project).count()
        + Poll.objects.filter(module__project=project).count()
        + Topic.objects.filter(module__project=project).count()
        + Subject.objects.filter(module__project=project).count()
        + Chapter.objects.filter(module__project=project).count()
    )


def _count_modules(project):
    """Count non-draft modules in a project."""
    return project.module_set.filter(is_draft=False).count()

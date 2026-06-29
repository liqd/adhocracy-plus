from django import template

from adhocracy4.comments.models import Comment
from adhocracy4.polls.models import Answer
from adhocracy4.polls.models import Poll
from adhocracy4.polls.models import Vote
from apps.debate.models import Subject
from apps.documents.models import Chapter
from apps.documents.models import Paragraph
from apps.ideas.models import Idea
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
            "contributions": 0,
            "modules": 0,
        }

    contributors = _get_project_contributors(project)

    return {
        "participants": len(contributors),
        "contributions": _count_contributions(project),
        "modules": _count_modules(project),
    }


def _get_project_contributors(project):
    """Get unique contributors for a project."""
    contributors = set()

    for idea in Idea.objects.filter(module__project=project):
        if idea.creator:
            contributors.add(idea.creator.id)

    _add_poll_contributors(project, contributors)

    for topic in Topic.objects.filter(module__project=project):
        if topic.creator:
            contributors.add(topic.creator.id)

    for subject in Subject.objects.filter(module__project=project):
        if subject.creator:
            contributors.add(subject.creator.id)

    _add_document_contributors(project, contributors)

    return contributors


def _add_poll_contributors(project, contributors):
    """Add poll voters and answerers to contributors set."""
    for poll in Poll.objects.filter(module__project=project):
        for question in poll.questions.all():
            for vote in Vote.objects.filter(choice__question=question):
                if vote.creator:
                    contributors.add(vote.creator.id)
            for answer in Answer.objects.filter(question=question):
                if answer.creator:
                    contributors.add(answer.creator.id)


def _add_document_contributors(project, contributors):
    """Add document commenters to contributors set."""
    for chapter in Chapter.objects.filter(module__project=project):
        for comment in Comment.objects.filter(
            content_type__model="chapter", object_pk=chapter.id
        ):
            if comment.creator:
                contributors.add(comment.creator.id)

        for paragraph in Paragraph.objects.filter(chapter=chapter):
            for comment in Comment.objects.filter(
                content_type__model="paragraph", object_pk=paragraph.id
            ):
                if comment.creator:
                    contributors.add(comment.creator.id)


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

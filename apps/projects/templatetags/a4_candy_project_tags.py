from django import template

from adhocracy4.comments.models import Comment
from apps.budgeting.models import Proposal as budget_proposal
from apps.ideas.models import Idea
from apps.interactiveevents.models import LiveQuestion
from apps.likes.models import Like
from apps.mapideas.models import MapIdea
from apps.polls.models import Vote

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
    item_count = \
        Idea.objects.filter(module=module).count() \
        + MapIdea.objects.filter(module=module).count() \
        + budget_proposal.objects.filter(module=module).count() \
        + Comment.objects.filter(idea__module=module).count() \
        + Comment.objects.filter(mapidea__module=module).count() \
        + Comment.objects.filter(budget_proposal__module=module).count() \
        + Comment.objects.filter(paragraph__chapter__module=module).count() \
        + Comment.objects.filter(chapter__module=module).count() \
        + Comment.objects.filter(poll__module=module).count() \
        + Comment.objects.filter(topic__module=module).count() \
        + Comment.objects.filter(subject__module=module).count() \
        + Vote.objects.filter(choice__question__poll__module=module).count() \
        + LiveQuestion.objects.filter(module=module).count() \
        + Like.objects.filter(question__module=module).count()

    return item_count

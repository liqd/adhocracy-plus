from django.utils.html import strip_tags

from adhocracy4.comments.models import Comment
from adhocracy4.polls.models import Vote
from apps.budgeting.models import Proposal as budget_proposal
from apps.ideas.models import Idea
from apps.interactiveevents.models import Like
from apps.interactiveevents.models import LiveQuestion
from apps.mapideas.models import MapIdea


def project_has_result_content(project) -> bool:
    return bool(strip_tags(project.result or "").strip())


def count_module_entries(module) -> int:
    """Count user-generated contributions for a participation module."""
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

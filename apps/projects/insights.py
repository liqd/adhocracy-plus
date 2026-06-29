from typing import Iterable
from typing import List

from django.core.exceptions import FieldDoesNotExist

from adhocracy4.polls.models import Answer
from adhocracy4.polls.models import Poll
from adhocracy4.polls.models import Vote
from adhocracy4.projects.models import Project
from adhocracy4.ratings.models import Rating
from apps.budgeting.models import Proposal
from apps.ideas.models import Idea
from apps.interactiveevents.models import Like
from apps.interactiveevents.models import LiveQuestion
from apps.mapideas.models import MapIdea
from apps.projects.helpers import get_all_comments_project
from apps.projects.models import ProjectInsight
from apps.topicprio.models import Topic


def create_insights(projects: Iterable[Project]) -> List[ProjectInsight]:
    return [create_insight(project=project) for project in projects]


def _collect_insight_metrics(project: Project) -> dict:
    """Collect participation metrics for a project without persisting."""
    modules = project.modules.all()

    ideas = Idea.objects.filter(module__in=modules)
    map_ideas = MapIdea.objects.filter(module__in=modules)
    comments = get_all_comments_project(project=project)
    proposals = Proposal.objects.filter(module__in=modules)
    polls = Poll.objects.filter(module__in=modules)
    votes = Vote.objects.filter(choice__question__poll__in=polls)
    answers = Answer.objects.filter(question__poll__in=polls)
    live_questions = LiveQuestion.objects.filter(module__in=modules)
    likes = Like.objects.filter(livequestion__in=live_questions)
    topics = Topic.objects.filter(module__in=modules)

    values = [Rating.POSITIVE, Rating.NEGATIVE]
    ratings_ideas = Rating.objects.filter(idea__in=ideas, value__in=values)
    ratings_map_ideas = Rating.objects.filter(mapidea__in=map_ideas, value__in=values)
    ratings_comments = Rating.objects.filter(comment__in=comments, value__in=values)
    ratings_topics = Rating.objects.filter(topic__in=topics, value__in=values)

    creator_objects = [
        comments,
        ratings_comments,
        ratings_ideas,
        ratings_map_ideas,
        ratings_topics,
        ideas,
        map_ideas,
        votes,
        answers,
        proposals,
    ]

    rating_objects = [
        ratings_comments,
        ratings_map_ideas,
        ratings_topics,
        ratings_ideas,
        likes,
    ]

    idea_objects = [ideas, map_ideas, proposals, topics]

    participant_user_ids = set()
    unregistered_participants = set()

    for obj in creator_objects:
        participant_user_ids.update(
            obj.filter(creator__isnull=False)
            .values_list("creator", flat=True)
            .distinct()
            .order_by()
        )
        if model_field_exists(obj.model, "content_id"):
            unregistered_participants.update(
                obj.filter(content_id__isnull=False)
                .values_list("content_id", flat=True)
                .distinct()
                .order_by()
            )

    return {
        "comments": comments.count(),
        "ratings": sum(queryset.count() for queryset in rating_objects),
        "written_ideas": sum(queryset.count() for queryset in idea_objects),
        "poll_answers": votes.count() + answers.count(),
        "live_questions": live_questions.count(),
        "participants": len(participant_user_ids) + len(unregistered_participants),
    }


def compute_insight_counts(project: Project) -> dict:
    """Return summary-style participation counts without persisting."""
    metrics = _collect_insight_metrics(project)
    return {
        "participants": metrics["participants"],
        "comments": metrics["comments"],
        "ratings": metrics["ratings"],
        "ideas": metrics["written_ideas"],
    }


def _sync_insight_participants(project: Project, insight: ProjectInsight) -> None:
    """Update active and unregistered participant counts on an insight."""
    modules = project.modules.all()

    ideas = Idea.objects.filter(module__in=modules)
    map_ideas = MapIdea.objects.filter(module__in=modules)
    comments = get_all_comments_project(project=project)
    proposals = Proposal.objects.filter(module__in=modules)
    polls = Poll.objects.filter(module__in=modules)
    votes = Vote.objects.filter(choice__question__poll__in=polls)
    answers = Answer.objects.filter(question__poll__in=polls)
    topics = Topic.objects.filter(module__in=modules)

    values = [Rating.POSITIVE, Rating.NEGATIVE]
    ratings_ideas = Rating.objects.filter(idea__in=ideas, value__in=values)
    ratings_map_ideas = Rating.objects.filter(mapidea__in=map_ideas, value__in=values)
    ratings_comments = Rating.objects.filter(comment__in=comments, value__in=values)
    ratings_topics = Rating.objects.filter(topic__in=topics, value__in=values)

    creator_objects = [
        comments,
        ratings_comments,
        ratings_ideas,
        ratings_map_ideas,
        ratings_topics,
        ideas,
        map_ideas,
        votes,
        answers,
        proposals,
    ]

    insight.active_participants.clear()
    unregistered_participants = set()

    for obj in creator_objects:
        ids = list(
            obj.filter(creator__isnull=False)
            .values_list("creator", flat=True)
            .distinct()
            .order_by()
        )
        insight.active_participants.add(*ids)
        if model_field_exists(obj.model, "content_id"):
            content_ids = set(
                obj.filter(content_id__isnull=False)
                .values_list("content_id", flat=True)
                .distinct()
                .order_by()
            )
            unregistered_participants = unregistered_participants.union(content_ids)

    insight.unregistered_participants = len(unregistered_participants)


def create_insight(project: Project) -> ProjectInsight:
    metrics = _collect_insight_metrics(project)
    insight, _ = ProjectInsight.objects.get_or_create(project=project)

    insight.comments = metrics["comments"]
    insight.ratings = metrics["ratings"]
    insight.written_ideas = metrics["written_ideas"]
    insight.poll_answers = metrics["poll_answers"]
    insight.live_questions = metrics["live_questions"]

    _sync_insight_participants(project, insight)
    insight.save()
    return insight


def model_field_exists(cls, field):
    try:
        cls._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False

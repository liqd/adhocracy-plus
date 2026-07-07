from typing import Iterable
from typing import List
from typing import Optional
from typing import Set

from django.core.exceptions import FieldDoesNotExist

from adhocracy4.comments.models import Comment
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

RATING_INSIGHT_VALUES = {Rating.POSITIVE, Rating.NEGATIVE}

INSIGHT_COUNT_FIELDS = (
    "comments",
    "ratings",
    "written_ideas",
    "poll_answers",
    "live_questions",
    "unregistered_participants",
)


def snapshot_insight_counts(insight: ProjectInsight) -> dict:
    counts = {field: getattr(insight, field) for field in INSIGHT_COUNT_FIELDS}
    counts["active_participants"] = insight.active_participants.count()
    return counts


def insight_count_changes(before: dict, after: dict) -> list[tuple[str, int, int]]:
    changes = []
    for field, old_value in before.items():
        new_value = after[field]
        if old_value != new_value:
            changes.append((field, old_value, new_value))
    return changes


def create_insights(projects: Iterable[Project]) -> List[ProjectInsight]:
    return [create_insight(project=project) for project in projects]


def rating_counts_toward_insights(value: Optional[int]) -> bool:
    return value in RATING_INSIGHT_VALUES


def module_counts_toward_insights(module) -> bool:
    return module is not None and not module.is_draft


def get_published_modules(project: Project):
    return project.modules.filter(is_draft=False)


def get_insight_module(obj) -> Optional[object]:
    if obj is None:
        return None
    if hasattr(obj, "module"):
        return obj.module
    if hasattr(obj, "poll"):
        return obj.poll.module
    return None


def comment_counts_toward_insights(comment: Comment) -> bool:
    if not comment.project_id:
        return False
    if comment.is_removed or comment.is_censored or comment.is_blocked:
        return False

    obj = comment.content_object
    while obj is not None:
        module = get_insight_module(obj)
        if module is not None:
            return module_counts_toward_insights(module)
        if hasattr(obj, "content_object"):
            obj = obj.content_object
        else:
            break
    return True


def get_counted_comments_project(project: Project):
    all_comments = get_all_comments_project(project=project)
    counted_pks = [
        comment.pk
        for comment in all_comments
        if comment_counts_toward_insights(comment)
    ]
    return all_comments.filter(pk__in=counted_pks)


def count_unregistered_participants(project: Project) -> int:
    polls = Poll.objects.filter(module__in=get_published_modules(project))
    votes = Vote.objects.filter(
        choice__question__poll__in=polls,
        creator__isnull=True,
        content_id__isnull=False,
    )
    answers = Answer.objects.filter(
        question__poll__in=polls,
        creator__isnull=True,
        content_id__isnull=False,
    )
    content_ids: Set[str] = set()
    content_ids.update(votes.values_list("content_id", flat=True).distinct())
    content_ids.update(answers.values_list("content_id", flat=True).distinct())
    return len(content_ids)


def sync_unregistered_participants(insight: ProjectInsight, project: Project) -> None:
    insight.unregistered_participants = count_unregistered_participants(project)
    insight.save(update_fields=["unregistered_participants"])


def add_active_participant(insight: ProjectInsight, user_id: Optional[int]) -> None:
    if user_id:
        insight.active_participants.add(user_id)


def create_insight(project: Project) -> ProjectInsight:
    modules = get_published_modules(project)

    ideas = Idea.objects.filter(module__in=modules)
    map_ideas = MapIdea.objects.filter(module__in=modules)
    comments = get_counted_comments_project(project=project)
    proposals = Proposal.objects.filter(module__in=modules)
    polls = Poll.objects.filter(module__in=modules)
    votes = Vote.objects.filter(choice__question__poll__in=polls)
    answers = Answer.objects.filter(question__poll__in=polls)
    live_questions = LiveQuestion.objects.filter(module__in=modules)
    likes = Like.objects.filter(livequestion__in=live_questions)
    topics = Topic.objects.filter(module__in=modules)

    values = list(RATING_INSIGHT_VALUES)
    ratings_ideas = Rating.objects.filter(idea__in=ideas, value__in=values)
    ratings_map_ideas = Rating.objects.filter(mapidea__in=map_ideas, value__in=values)
    ratings_comments = Rating.objects.filter(comment__in=comments, value__in=values)
    ratings_topics = Rating.objects.filter(topic__in=topics, value__in=values)
    ratings_proposals = Rating.objects.filter(
        budget_proposal__in=proposals, value__in=values
    )

    creator_objects = [
        comments,
        ratings_comments,
        ratings_ideas,
        ratings_map_ideas,
        ratings_topics,
        ratings_proposals,
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
        ratings_proposals,
        likes,
    ]

    idea_objects = [ideas, map_ideas, proposals, topics]

    insight, _ = ProjectInsight.objects.get_or_create(project=project)

    insight.comments = comments.count()
    insight.ratings = sum(x.count() for x in rating_objects)
    insight.written_ideas = sum(x.count() for x in idea_objects)
    insight.poll_answers = votes.count() + answers.count()
    insight.live_questions = live_questions.count()

    insight.active_participants.clear()
    unregistered_participants = set()

    for obj in creator_objects:
        # ignore objects which don't have a creator, they are counted in the next step.
        ids = list(
            obj.filter(creator__isnull=False)
            .values_list("creator", flat=True)
            .distinct()
            .order_by()
        )
        insight.active_participants.add(*ids)
        # content from unregistered users doesn't have a creator but a content_id
        if model_field_exists(obj.model, "content_id"):
            content_ids = set(
                obj.filter(content_id__isnull=False)
                .values_list("content_id", flat=True)
                .distinct()
                .order_by()
            )
            unregistered_participants = unregistered_participants.union(content_ids)

    insight.unregistered_participants = len(unregistered_participants)
    insight.save()
    return insight


def model_field_exists(cls, field):
    try:
        cls._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False


def user_has_active_contributions(project: Project, user_id: int) -> bool:
    """Return whether the user still has contributions counted as participation.

    Mirrors the creator_objects logic in create_insight: ideas, map ideas,
    proposals, comments, poll votes/answers, and positive/negative ratings on
    project content.
    """
    modules = get_published_modules(project)
    comments = get_counted_comments_project(project=project)
    polls = Poll.objects.filter(module__in=modules)
    ideas = Idea.objects.filter(module__in=modules)
    map_ideas = MapIdea.objects.filter(module__in=modules)
    topics = Topic.objects.filter(module__in=modules)
    proposals = Proposal.objects.filter(module__in=modules)
    values = list(RATING_INSIGHT_VALUES)

    existence_checks = (
        Idea.objects.filter(module__in=modules, creator_id=user_id),
        MapIdea.objects.filter(module__in=modules, creator_id=user_id),
        Proposal.objects.filter(module__in=modules, creator_id=user_id),
        comments.filter(creator_id=user_id),
        Vote.objects.filter(choice__question__poll__in=polls, creator_id=user_id),
        Answer.objects.filter(question__poll__in=polls, creator_id=user_id),
        Rating.objects.filter(creator_id=user_id, idea__in=ideas, value__in=values),
        Rating.objects.filter(
            creator_id=user_id, mapidea__in=map_ideas, value__in=values
        ),
        Rating.objects.filter(
            creator_id=user_id, comment__in=comments, value__in=values
        ),
        Rating.objects.filter(creator_id=user_id, topic__in=topics, value__in=values),
        Rating.objects.filter(
            creator_id=user_id, budget_proposal__in=proposals, value__in=values
        ),
    )
    return any(qs.exists() for qs in existence_checks)


def remove_active_participant_if_inactive(
    insight: ProjectInsight, project: Project, user_id: int
) -> None:
    """Remove a user from active_participants when they have no contributions left.

    Called after a contribution is deleted. A user may author many objects, so
    we only remove them once user_has_active_contributions returns False.
    """
    if not user_id:
        return
    if not insight.active_participants.filter(pk=user_id).exists():
        return
    if user_has_active_contributions(project=project, user_id=user_id):
        return
    insight.active_participants.remove(user_id)

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

# Project insights are stored as cached counters on ProjectInsight and updated
# incrementally via signals (apps/projects/signals.py).
#
# Helpers in this module define which content counts toward those numbers.
# create_insight() uses them for full recounts; signals use them to decide
# whether to increment or decrement on create, update, or delete.
#
# Not every row in the database counts: e.g. soft-deleted comments, draft
# modules, archived proposals, hidden live questions, and neutral ratings
# (value 0) are excluded.

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
    """Capture current cached counts for comparison before a recount."""
    counts = {field: getattr(insight, field) for field in INSIGHT_COUNT_FIELDS}
    counts["active_participants"] = insight.active_participants.count()
    return counts


def insight_count_changes(before: dict, after: dict) -> list[tuple[str, int, int]]:
    """Return fields that changed between two snapshots (for command output)."""
    changes = []
    for field, old_value in before.items():
        new_value = after[field]
        if old_value != new_value:
            changes.append((field, old_value, new_value))
    return changes


def create_insights(projects: Iterable[Project]) -> List[ProjectInsight]:
    return [create_insight(project=project) for project in projects]


def rating_counts_toward_insights(value: Optional[int]) -> bool:
    """Return whether a rating value should increment the insights ratings counter.

    Users can "remove" a rating by setting value to 0 without deleting the row.
    Only thumbs up/down (±1) count, matching create_insight() and update_rating_count.
    """
    return value in RATING_INSIGHT_VALUES


def module_counts_toward_insights(module) -> bool:
    """Return whether content on this module should affect insights.

    Draft modules are hidden from participants; their content is excluded
    until the module is published (see refresh_insights_on_module_draft_change).
    """
    return module is not None and not module.is_draft


def written_idea_counts_toward_insights(item) -> bool:
    """Return whether an idea-like object counts toward insight.written_ideas.

    Archived budgeting proposals are excluded (same as create_insight recount).
    """
    if not module_counts_toward_insights(item.module):
        return False
    if isinstance(item, Proposal) and item.is_archived:
        return False
    return True


def live_question_counts_toward_insights(live_question: LiveQuestion) -> bool:
    """Return whether a live question counts toward insight.live_questions."""
    if live_question.is_hidden:
        return False
    return module_counts_toward_insights(live_question.module)


def get_published_modules(project: Project):
    """Modules whose content is included in insight counts and participant lists."""
    return project.modules.filter(is_draft=False)


def get_insight_module(obj) -> Optional[object]:
    """Resolve the module for a content object (idea, poll, proposal, etc.).

    Used when the object does not carry a module FK directly, e.g. comments
    attach to many types via GenericForeignKey.
    """
    if obj is None:
        return None
    if hasattr(obj, "module"):
        return obj.module
    if hasattr(obj, "poll"):
        return obj.poll.module
    return None


def comment_counts_toward_insights(comment: Comment) -> bool:
    """Return whether this comment should count toward insight.comments.

    Comments are soft-deleted (is_removed / is_censored) or blocked rather than
    removed from the DB, so post_delete never runs. Signals call this on every
    save to detect when a comment enters or leaves the counted set.

    Also skips comments on draft modules by walking up to the parent content
    (idea, proposal, poll, or nested comment).
    """
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
    """Comments that should contribute to insight.comments for a full recount.

    Wraps get_all_comments_project() and applies comment_counts_toward_insights
    so create_insight() matches what signals increment/decrement.
    """
    all_comments = get_all_comments_project(project=project)
    counted_pks = [
        comment.pk
        for comment in all_comments
        if comment_counts_toward_insights(comment)
    ]
    return all_comments.filter(pk__in=counted_pks)


def count_unregistered_participants(project: Project) -> int:
    """Count distinct anonymous voters by content_id on published poll modules.

    Used instead of += 1 on each vote so one browser session is one participant
    even if they submit multiple Vote/Answer rows.
    """
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
    """Recompute unregistered_participants from the database.

    Called after anonymous poll votes are created or deleted; the integer field
    cannot be decremented safely without knowing unique content_ids.
    """
    insight.unregistered_participants = count_unregistered_participants(project)
    insight.save(update_fields=["unregistered_participants"])


def add_active_participant(insight: ProjectInsight, user_id: Optional[int]) -> None:
    """Add a user to active_participants if they have a creator account.

    No-op for anonymous participation (polls) or missing creator_id.
    """
    if user_id:
        insight.active_participants.add(user_id)


def _collect_insight_metrics(project: Project) -> dict:
    """Collect participation metrics for a project without persisting."""
    modules = get_published_modules(project)

    ideas = Idea.objects.filter(module__in=modules)
    map_ideas = MapIdea.objects.filter(module__in=modules)
    comments = get_counted_comments_project(project=project)
    proposals = Proposal.objects.filter(module__in=modules, is_archived=False)
    polls = Poll.objects.filter(module__in=modules)
    votes = Vote.objects.filter(choice__question__poll__in=polls)
    answers = Answer.objects.filter(question__poll__in=polls)
    live_questions = LiveQuestion.objects.filter(module__in=modules, is_hidden=False)
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

    idea_objects = [ideas, map_ideas, proposals]

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
    modules = get_published_modules(project)

    ideas = Idea.objects.filter(module__in=modules)
    map_ideas = MapIdea.objects.filter(module__in=modules)
    comments = get_counted_comments_project(project=project)
    proposals = Proposal.objects.filter(module__in=modules, is_archived=False)
    polls = Poll.objects.filter(module__in=modules)
    votes = Vote.objects.filter(choice__question__poll__in=polls)
    answers = Answer.objects.filter(question__poll__in=polls)
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
    """Rebuild all insight counters for a project from scratch.

    Authoritative when signals may have drifted; used by reset_insights_table.
    Uses the same inclusion rules as the signal helpers (published modules,
    visible comments, ±1 ratings, etc.).
    """
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
    proposals = Proposal.objects.filter(module__in=modules, is_archived=False)
    values = list(RATING_INSIGHT_VALUES)

    existence_checks = (
        Idea.objects.filter(module__in=modules, creator_id=user_id),
        MapIdea.objects.filter(module__in=modules, creator_id=user_id),
        Proposal.objects.filter(
            module__in=modules, creator_id=user_id, is_archived=False
        ),
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

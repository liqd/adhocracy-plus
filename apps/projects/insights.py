from typing import Iterable
from typing import List

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


def create_insight(project: Project) -> ProjectInsight:
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
        topics,
        polls,
    ]

    rating_objects = [
        ratings_comments,
        ratings_map_ideas,
        ratings_topics,
        ratings_ideas,
        likes,
    ]

    insight, _ = ProjectInsight.objects.update_or_create(
        project=project,
        comments=comments.count(),
        ratings=sum(x.count() for x in rating_objects),
        written_ideas=sum(x.count() for x in [ideas, map_ideas, proposals, topics]),
        poll_answers=votes.count() + answers.count(),
        live_questions=live_questions.count(),
    )

    for obj in creator_objects:
        ids = list(obj.values_list("creator", flat=True).distinct().order_by())
        insight.active_participants.add(*ids)

    return insight

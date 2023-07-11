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
from apps.topicprio.models import Topic


def query_statistics_for_project(project: Project):
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

    count_comments = comments.count()
    count_ratings = ratings_comments.count()
    count_ideas = 0
    count_poll_answers = 0
    count_event_questions = 0

    creator_objects = [
        comments,
        ratings_comments,
        ideas,
        ratings_ideas,
        map_ideas,
        ratings_map_ideas,
        votes,
        answers,
        topics,
        proposals,
    ]

    count_ideas += ideas.count()
    count_ratings += ratings_ideas.count()
    count_ideas += map_ideas.count()
    count_poll_answers += votes.count() + answers.count()
    count_ratings += ratings_map_ideas.count()
    count_event_questions += live_questions.count()
    count_ratings += likes.count()
    count_ratings += ratings_topics.count()
    count_ideas += proposals.count()

    creators_ids = set()
    for x in creator_objects:
        creators_ids.update(set(x.values_list("creator", flat=True)))

    count_creators = len(creators_ids)

    counts = {
        "active participants": count_creators,
        "comments": count_comments,
        "ratings": count_ratings,
        "written ideas": count_ideas,
        "poll answers": count_poll_answers,
        "interactive event questions": count_event_questions,
    }

    return counts

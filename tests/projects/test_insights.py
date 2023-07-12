import pytest

from apps.projects.insights import create_insight
from apps.projects.models import ProjectInsight

get_insight = ProjectInsight.objects.get


@pytest.mark.django_db
def test_can_create_insight_for_empty_project(
    project_factory,
):
    project = project_factory()
    assert not hasattr(project, "insight")

    create_insight(project=project)
    assert hasattr(project, "insight")


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [create_insight, get_insight])
def test_comments_of_comments_are_counted(
    module_factory,
    comment_factory,
    idea_factory,
    user_factory,
    insight_provider,
):
    module = module_factory()
    users = user_factory.create_batch(size=4)
    ideas = [
        idea_factory(module=module, creator=users[0]),
        idea_factory(module=module, creator=users[1]),
        idea_factory(module=module, creator=users[2]),
        idea_factory(module=module, creator=users[3]),
    ]
    comment = comment_factory(content_object=ideas[0], creator=users[0])
    comments = [
        comment_factory(content_object=comment, creator=users[0]),
        comment_factory(content_object=comment, creator=users[1]),
        comment_factory(content_object=comment, creator=users[2]),
        comment_factory(content_object=ideas[3], creator=users[3]),
    ]

    insight = insight_provider(project=module.project)

    assert insight.written_ideas == len(ideas)
    assert insight.comments == len(comments) + 1
    assert insight.active_participants.count() == len(users)


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [create_insight, get_insight])
def test_repeated_saving_does_not_increase_count(
    module_factory,
    live_question_factory,
    rating_factory,
    insight_provider,
):
    module = module_factory()
    live_question = live_question_factory(module=module)
    rating = rating_factory(content_object=live_question)

    live_question.save()
    rating.value = 0
    rating.save()

    insight = insight_provider(project=module.project)

    assert insight.comments == 0


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [create_insight, get_insight])
def test_initiators_are_not_counted_as_participants(
    module_factory,
    poll_factory,
    topic_factory,
    insight_provider,
):
    module = module_factory()
    topic_factory(module=module)
    poll_factory(module=module)
    insight = insight_provider(project=module.project)

    assert insight.active_participants.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [create_insight, get_insight])
def test_complex_example(
    project_factory,
    module_factory,
    user_factory,
    topic_factory,
    live_question_factory,
    like_factory,
    rating_factory,
    comment_factory,
    poll_factory,
    question_factory,
    choice_factory,
    answer_factory,
    vote_factory,
    insight_provider,
):
    project = project_factory(name="complex_example")
    modules = module_factory.create_batch(size=2, project=project)
    users = user_factory.create_batch(size=5)
    topics = topic_factory.create_batch(size=7, module=modules[0])
    comments = comment_factory.create_batch(
        size=3,
        content_object=topics[0],
        creator=users[1],
    )
    poll = poll_factory(module=modules[1])
    question = question_factory(poll=poll, is_open=True)

    answers = [
        answer_factory(question=question, creator=users[0]),
        answer_factory(question=question, creator=users[1]),
    ]

    question = question_factory(poll=poll, multiple_choice=True)
    choices = choice_factory.create_batch(size=3, question=question)
    votes = [
        vote_factory(choice=choices[0], creator=users[3]),
        vote_factory(choice=choices[1], creator=users[4]),
        vote_factory(choice=choices[2], creator=users[1]),
    ]

    comments += comment_factory.create_batch(
        size=8,
        content_object=poll,
        creator=users[2],
    )

    ratings = [
        rating_factory(content_object=comments[2], creator=users[0]),
        rating_factory(content_object=comments[3], creator=users[1]),
        rating_factory(content_object=comments[4], creator=users[0]),
    ]

    live_questions = [
        live_question_factory(module=modules[1], creator=users[3]),
        live_question_factory(module=modules[1], creator=users[4]),
        live_question_factory(module=modules[1], creator=users[1]),
    ]

    likes = [
        like_factory(livequestion=live_questions[0]),
        like_factory(livequestion=live_questions[1]),
        like_factory(livequestion=live_questions[2]),
    ]

    insight = insight_provider(project=project)

    assert insight.live_questions == len(live_questions)
    assert insight.written_ideas == len(topics)
    assert insight.comments == len(comments)
    assert insight.poll_answers == len(answers) + len(votes)
    assert insight.ratings == len(ratings) + len(likes)
    assert insight.active_participants.count() == len(users)


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [get_insight])
def test_create_insight_for_ideas(
    module_factory,
    idea_factory,
    topic_factory,
    comment_factory,
    rating_factory,
    user_factory,
    insight_provider,
):
    module = module_factory()
    users = user_factory.create_batch(size=5)
    topic = topic_factory(module=module, creator=users[0])
    idea = idea_factory(module=module, creator=users[2])

    comment = comment_factory(content_object=idea, creator=users[1])
    comment_factory(content_object=comment, creator=users[2])
    comment_factory(content_object=idea, creator=users[3])
    rating_factory(content_object=comment, creator=users[4])
    rating_factory(content_object=comment, creator=users[3])
    rating_factory(content_object=topic, creator=users[4])

    insight = insight_provider(project=module.project)

    assert insight.written_ideas == 2
    assert insight.poll_answers == 0
    assert insight.live_questions == 0
    assert insight.ratings == 3
    assert insight.comments == 3
    assert insight.active_participants.count() == 4

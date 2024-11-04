import pytest
from django.urls import reverse
from rest_framework import status

from adhocracy4.polls import phases
from adhocracy4.polls.models import Poll
from adhocracy4.polls.models import Vote
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from apps.dashboard.blueprints import blueprints
from apps.projects.insights import create_insight
from apps.projects.models import ProjectInsight
from apps.projects.models import create_insight_context

get_insight = ProjectInsight.objects.get


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [create_insight, get_insight])
def test_draft_modules_do_not_trigger_show_results(
    project_factory,
    module_factory,
    poll_factory,
    insight_provider,
    question_factory,
    answer_factory,
):
    n_answers = 2
    expected_label = "poll answers"

    project = project_factory()
    module = module_factory(project=project, is_draft=False, blueprint_type="PO")
    poll = poll_factory(module=module)
    question = question_factory(poll=poll, is_open=True)
    answer_factory.create_batch(size=n_answers, question=question)

    insight = insight_provider(project=project)

    assert insight.poll_answers == n_answers

    context = create_insight_context(insight=insight)
    labels = [label for label, count in context["counts"]]

    assert expected_label in labels

    module.is_draft = True
    module.save()
    insight = insight_provider(project=project)
    context = create_insight_context(insight=insight)
    labels = [label for label, count in context["counts"]]

    assert expected_label not in labels


@pytest.mark.django_db
@pytest.mark.parametrize("module_name", ["brainstorming", "poll", "interactive-event"])
def test_create_insight_context(
    module_name,
    module_factory,
):
    expected_label = {
        "brainstorming": "written ideas",
        "poll": "poll answers",
        "interactive-event": "interactive event questions",
    }

    blueprint_type = None
    for blueprint in blueprints:
        if blueprint[0] == module_name:
            blueprint_type = blueprint[1].type
            break

    assert blueprint_type

    module = module_factory(blueprint_type=blueprint_type)
    insight = create_insight(project=module.project)
    context = create_insight_context(insight=insight)

    labels = [label for label, count in context["counts"]]

    assert expected_label[module_name] in labels


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


@pytest.mark.django_db
@pytest.mark.parametrize("insight_provider", [create_insight, get_insight])
def test_create_insight_contexts_combines_unregistered_users_and_registered_users(
    apiclient,
    user_factory,
    phase_factory,
    poll_factory,
    choice_factory,
    question_factory,
    insight_provider,
):
    phase, module, project, _ = setup_phase(
        phase_factory, poll_factory, phases.VotingPhase
    )

    poll = Poll.objects.first()
    poll.allow_unregistered_users = True
    poll.save()
    question = question_factory(poll=poll)
    choice1 = choice_factory(question=question)
    choice_factory(question=question)
    open_question = question_factory(poll=poll, is_open=True)

    assert Vote.objects.count() == 0

    url = reverse("polls-vote", kwargs={"pk": poll.pk})

    users = user_factory.create_batch(size=4)
    n_unregistered_users = 2
    with freeze_phase(phase):
        for i in range(n_unregistered_users):
            data = {
                "votes": {
                    question.pk: {
                        "choices": [choice1.pk],
                        "other_choice_answer": "",
                        "open_answer": "",
                    },
                    open_question.pk: {
                        "choices": [],
                        "other_choice_answer": "",
                        "open_answer": "an open answer",
                    },
                },
                "agreed_terms_of_use": True,
                "captcha": "testpass:1",
            }
            response = apiclient.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED

        for user in users:
            apiclient.force_authenticate(user=user)
            data = {
                "votes": {
                    question.pk: {
                        "choices": [choice1.pk],
                        "other_choice_answer": "",
                        "open_answer": "",
                    },
                    open_question.pk: {
                        "choices": [],
                        "other_choice_answer": "",
                        "open_answer": "an open answer",
                    },
                },
                "agreed_terms_of_use": True,
            }
            response = apiclient.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED

    insight = insight_provider(project=project)
    assert insight.active_participants.count() == len(users)
    assert insight.unregistered_participants == n_unregistered_users
    context = create_insight_context(insight)
    assert context["counts"][0][1] == len(users) + n_unregistered_users

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_moderator_can_view_moderation_projects(client,
                                                project_factory):
    project = project_factory()
    moderator = project.moderators.first()
    client.login(username=moderator.email, password='password')
    url = reverse('moderationprojects-list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert project.name == response.data[0]['title']


@pytest.mark.django_db
def test_anonymous_cannot_view_moderation_projects(client):
    url = reverse('moderationprojects-list')
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderation_projects_sorted(client,
                                    comment_factory,
                                    idea_factory,
                                    user_classification_factory,
                                    ai_classification_factory):
    idea_0 = idea_factory()
    project_0 = idea_0.module.project
    num_user_classifications_0 = 1
    num_ai_classifications_0 = 0

    idea_1 = idea_factory()
    project_1 = idea_1.module.project
    num_user_classifications_1 = 2
    num_ai_classifications_1 = 2

    idea_2 = idea_factory()
    project_2 = idea_2.module.project
    num_user_classifications_2 = 1
    num_ai_classifications_2 = 2

    moderator = project_0.moderators.first()
    project_1.moderators.add(moderator)
    project_2.moderators.add(moderator)

    for i in range(3):
        for j in range(locals()['num_user_classifications_{}'.format(i)]):
            comment = comment_factory(
                content_object=locals()['idea_{}'.format(i)])
            user_classification = user_classification_factory(comment=comment)
        for k in range(locals()['num_ai_classifications_{}'.format(i)]):
            comment = comment_factory(
                content_object=locals()['idea_{}'.format(i)])
            user_classification = ai_classification_factory(comment=comment)

    client.login(username=moderator.email, password='password')
    url = reverse('moderationprojects-list')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3

    project_data_0 = response.data[0]
    project_data_1 = response.data[1]
    project_data_2 = response.data[2]

    assert project_1.name == project_data_0['title']
    assert num_user_classifications_1 + num_ai_classifications_1 == \
           project_data_0['offensive']

    assert project_2.name == project_data_1['title']
    assert num_user_classifications_2 + num_ai_classifications_2 == \
           project_data_1['offensive']

    assert project_0.name == project_data_2['title']
    assert num_user_classifications_0 + num_ai_classifications_0 == \
           project_data_2['offensive']

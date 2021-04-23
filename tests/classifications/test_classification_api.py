import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_anonymous_cannot_view_classifications(apiclient, project):
    user_classifications_url = reverse('userclassifications-list',
                                       kwargs={'project_pk': project.pk})
    response = apiclient.get(user_classifications_url)
    assert response.status_code == 403

    ai_classifications_url = reverse('aiclassifications-list',
                                     kwargs={'project_pk': project.pk})
    response = apiclient.get(ai_classifications_url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_wrong_moderator_cannot_view_classifications(apiclient,
                                                     project_factory):
    project_1 = project_factory()
    project_2 = project_factory()

    moderator = project_1.moderators.first()
    apiclient.login(username=moderator.email, password='password')

    user_classifications_url = reverse('userclassifications-list',
                                       kwargs={'project_pk': project_2.pk})
    response = apiclient.get(user_classifications_url)
    assert response.status_code == 403

    ai_classifications_url = reverse('aiclassifications-list',
                                     kwargs={'project_pk': project_2.pk})
    response = apiclient.get(ai_classifications_url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_view_classifications(apiclient,
                                            ai_classification_factory,
                                            user_classification_factory,
                                            comment_factory,
                                            idea):
    comment_1 = comment_factory(content_object=idea)
    comment_2 = comment_factory(content_object=idea)
    comment_text_1 = comment_1.comment
    comment_text_2 = comment_2.comment
    user_classification = user_classification_factory(comment=comment_1)
    ai_classification = ai_classification_factory(comment=comment_2)
    project = idea.project
    moderator = project.moderators.first()
    apiclient.login(username=moderator.email, password='password')

    user_classifications_url = reverse('userclassifications-list',
                                       kwargs={'project_pk': project.pk})
    response = apiclient.get(user_classifications_url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert comment_text_1 in response.data[0].values()
    assert comment_1.get_absolute_url() in response.data[0]['comment'].values()
    assert user_classification.get_classification_display() in \
           response.data[0].values()

    ai_classifications_url = reverse('aiclassifications-list',
                                     kwargs={'project_pk': project.pk})
    response = apiclient.get(ai_classifications_url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert comment_text_2 in response.data[0].values()
    assert comment_2.get_absolute_url() in response.data[0]['comment'].values()
    assert ai_classification.get_classification_display() in \
           response.data[0].values()

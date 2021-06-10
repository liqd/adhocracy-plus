import pytest
from django.urls import reverse
from rest_framework import status

from apps.ideas import phases
from apps.ideas.models import Idea
from tests.helpers import freeze_phase
from tests.helpers import freeze_post_phase
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_idea_list_api(idea_factory, apiclient):
    idea_1 = idea_factory()
    module = idea_1.module
    idea_2 = idea_factory(module=module)
    idea_3 = idea_factory(module=module)
    idea_other_module = idea_factory()

    assert module != idea_other_module.module

    url = reverse('ideas-list',
                  kwargs={'module_pk': module.pk})
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == idea_1.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == idea_2.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == idea_3.pk)])
    assert not any([True for dict in response.data
                   if ('pk' in dict and dict['pk'] == idea_other_module.pk)])


@pytest.mark.django_db
def test_idea_serializer(idea_factory, comment_factory, apiclient):
    idea = idea_factory(
        description='<p>description with a <strong>bold</strong> bit</p>'
    )
    comment = comment_factory(content_object=idea)
    comment_factory(content_object=idea)
    comment_factory(content_object=idea)
    comment_factory(content_object=idea)
    comment_factory(content_object=comment)

    url = reverse('ideas-list',
                  kwargs={'module_pk': idea.module.pk})
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert response.data[0]['description'] == 'description with a bold bit'
    assert response.data[0]['comment_count'] == 4


@pytest.mark.django_db
def test_anonymous_cannot_add_idea(apiclient, idea):
    url = reverse('ideas-list',
                  kwargs={'module_pk': idea.module.pk})
    data = {}
    response = apiclient.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_initiator_can_add_idea(
        apiclient, admin, phase_factory, idea_factory,
        category_factory, label_factory):
    phase, module, project, _ = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse('ideas-list',
                  kwargs={'module_pk': module.pk})
    category = category_factory(module=module)
    label = label_factory(module=module)
    data = {
        "name": "an idea",
        "description": "this is the description",
        "category_pk": category.pk,
        "labels": [label.pk]
    }
    user = project.organisation.initiators.first()
    apiclient.force_authenticate(user=user)
    response = apiclient.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Idea.objects.get(
        name=data['name']).description == data['description']


@pytest.mark.django_db
def test_user_can_add_idea_during_phase(
        apiclient, user, phase_factory, idea_factory,
        category_factory, label_factory):
    phase, module, project, _ = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse('ideas-list',
                  kwargs={'module_pk': module.pk})
    category = category_factory(module=module)
    label = label_factory(module=module)
    data = {
        "name": "an idea",
        "description": "this is the description",
        "category_pk": category.pk,
        "labels": [label.pk]
    }
    apiclient.force_authenticate(user=user)
    with freeze_phase(phase):
        response = apiclient.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Idea.objects.get(
            name=data['name']).description == data['description']


@pytest.mark.django_db
def test_user_cannot_add_idea_after_phase(
        apiclient, user, phase_factory, idea_factory,
        category_factory, label_factory):
    phase, module, project, _ = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse('ideas-list',
                  kwargs={'module_pk': module.pk})
    category = category_factory(module=module)
    label = label_factory(module=module)
    data = {
        "name": "an idea",
        "description": "this is the description",
        "category_pk": category.pk,
        "labels": [label.pk]
    }
    apiclient.force_authenticate(user=user)
    with freeze_post_phase(phase):
        response = apiclient.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_initiator_can_update_idea(apiclient, idea):
    url = reverse('ideas-detail',
                  kwargs={'module_pk': idea.module.pk,
                          'pk': idea.pk})
    data = {
        "name": "a changed idea",
        "description": "this is the changed description",
    }
    user = idea.module.project.organisation.initiators.first()
    apiclient.force_authenticate(user=user)
    response = apiclient.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    idea = Idea.objects.first()
    assert idea.name == data['name']
    assert idea.description == data['description']


@pytest.mark.django_db
def test_user_can_update_idea_during_phase(
        apiclient, phase_factory, idea_factory):
    phase, _, project, item = setup_phase(phase_factory, idea_factory,
                                          phases.CollectPhase)
    url = reverse('ideas-detail',
                  kwargs={'module_pk': item.module.pk,
                          'pk': item.pk})
    data = {
        "name": "a changed idea",
        "description": "this is the changed description",
    }
    user = item.creator
    apiclient.force_authenticate(user=user)
    with freeze_phase(phase):
        response = apiclient.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        idea = Idea.objects.first()
        assert idea.name == data['name']
        assert idea.description == data['description']


@pytest.mark.django_db
def test_user_cannot_update_idea_after_phase(
        apiclient, phase_factory, idea_factory):
    phase, _, project, item = setup_phase(phase_factory, idea_factory,
                                          phases.CollectPhase)
    url = reverse('ideas-detail',
                  kwargs={'module_pk': item.module.pk,
                          'pk': item.pk})
    data = {
        "name": "a changed idea",
        "description": "this is the changed description",
    }
    user = item.creator
    apiclient.force_authenticate(user=user)
    with freeze_post_phase(phase):
        response = apiclient.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

import pytest
from dateutil.parser import parse
from django.urls import reverse

from tests.helpers import freeze_phase
from tests.helpers import freeze_post_phase


@pytest.mark.django_db
def test_app_module_api(project_factory, module_factory, apiclient):
    project_1 = project_factory(is_app_accessible=True)
    project_2 = project_factory(is_app_accessible=True)
    project_3 = project_factory(is_app_accessible=True)
    project_4 = project_factory(is_app_accessible=False)
    module_1 = module_factory(project=project_1)
    module_2 = module_factory(project=project_2)
    module_3 = module_factory(project=project_3)
    module_4 = module_factory(project=project_3)
    module_5 = module_factory(project=project_3, is_draft=True)
    module_6 = module_factory(project=project_4)

    url = reverse('app-modules-list')
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == module_1.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == module_2.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == module_3.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == module_4.pk)])
    assert not any([True for dict in response.data
                   if ('pk' in dict and dict['pk'] == module_5.pk)])
    assert not any([True for dict in response.data
                   if ('pk' in dict and dict['pk'] == module_6.pk)])


@pytest.mark.django_db
def test_app_module_api_agenda_setting(
        client, apiclient, project_factory,
        category_factory, label_factory):
    project = project_factory(is_app_accessible=True)
    organisation = project.organisation
    initiator = organisation.initiators.first()
    url = reverse('a4dashboard:module-create',
                  kwargs={'organisation_slug': organisation.slug,
                          'project_slug': project.slug,
                          'blueprint_slug': 'agenda-setting'
                          })
    client.login(username=initiator.email, password='password')
    response = client.post(url)
    assert project.modules.count() == 1
    module = project.modules[0]
    module.is_draft = False
    module.save()
    category_1 = category_factory(module=module)
    category_2 = category_factory(module=module)
    label_1 = label_factory(module=module)
    label_2 = label_factory(module=module)

    url = reverse('app-modules-list')
    response = apiclient.get(url, format='json')
    assert response.data[0]['phases'][0]['is_active'] is False
    assert response.data[0]['phases'][1]['is_active'] is False

    assert len(project.modules[0].phases) == 2
    collect_phase = module.phases.get(type='a4_candy_ideas:collect')
    collect_phase.start_date = parse('2021-07-07 7:10:00 UTC')
    collect_phase.end_date = parse('2021-07-07 12:10:00 UTC')
    collect_phase.save()

    rating_phase = module.phases.get(type='a4_candy_ideas:rating')
    rating_phase.start_date = parse('2021-07-07 12:10:00 UTC')
    rating_phase.end_date = parse('2021-07-07 20:10:00 UTC')
    rating_phase.save()

    response = apiclient.get(url, format='json')
    assert response.status_code == 200
    assert response.data[0]['pk'] == module.pk
    assert (category_1.pk, category_1.name) in response.data[0]['categories']
    assert (category_2.pk, category_2.name) in response.data[0]['categories']
    assert (label_1.pk, label_1.name) in response.data[0]['labels']
    assert (label_2.pk, label_2.name) in response.data[0]['labels']
    assert len(response.data[0]['phases']) == 2

    with freeze_phase(collect_phase):
        response = apiclient.get(url, format='json')
        assert response.data[0]['ideas_collect_phase_active'] is True
        assert response.data[0]['phases'][0]['name'] == 'Collect phase'
        assert response.data[0]['phases'][0]['is_active'] is True
        assert response.data[0]['phases'][1]['name'] == 'Rating phase'
        assert response.data[0]['phases'][1]['is_active'] is False

    with freeze_phase(rating_phase):
        response = apiclient.get(url, format='json')
        assert response.data[0]['ideas_collect_phase_active'] is False
        assert response.data[0]['phases'][0]['name'] == 'Collect phase'
        assert response.data[0]['phases'][0]['is_active'] is False
        assert response.data[0]['phases'][1]['name'] == 'Rating phase'
        assert response.data[0]['phases'][1]['is_active'] is True

    with freeze_post_phase(rating_phase):
        response = apiclient.get(url, format='json')
        assert response.data[0]['ideas_collect_phase_active'] is False
        assert response.data[0]['phases'][0]['name'] == 'Collect phase'
        assert response.data[0]['phases'][0]['is_active'] is False
        assert response.data[0]['phases'][1]['name'] == 'Rating phase'
        assert response.data[0]['phases'][1]['is_active'] is False


@pytest.mark.django_db
def test_app_module_api_poll(
        client, apiclient, project_factory):
    project = project_factory(is_app_accessible=True)
    organisation = project.organisation
    initiator = organisation.initiators.first()
    url = reverse('a4dashboard:module-create',
                  kwargs={'organisation_slug': organisation.slug,
                          'project_slug': project.slug,
                          'blueprint_slug': 'poll'
                          })
    client.login(username=initiator.email, password='password')
    response = client.post(url)
    assert project.modules.count() == 1
    module = project.modules[0]
    module.is_draft = False
    module.save()

    url = reverse('app-modules-list')
    response = apiclient.get(url, format='json')
    assert response.data[0]['phases'][0]['is_active'] is False

    assert len(project.modules[0].phases) == 1
    phase = module.phases[0]
    phase.start_date = parse('2021-07-07 7:10:00 UTC')
    phase.end_date = parse('2021-07-07 12:10:00 UTC')
    phase.save()

    response = apiclient.get(url, format='json')
    assert response.status_code == 200
    assert response.data[0]['pk'] == module.pk
    assert response.data[0]['labels'] is False
    assert response.data[0]['categories'] is False
    assert len(response.data[0]['phases']) == 1

    with freeze_phase(phase):
        response = apiclient.get(url, format='json')
        assert response.data[0]['ideas_collect_phase_active'] is False
        assert response.data[0]['phases'][0]['name'] == 'Voting phase'
        assert response.data[0]['phases'][0]['is_active'] is True

    with freeze_post_phase(phase):
        response = apiclient.get(url, format='json')
        assert response.data[0]['ideas_collect_phase_active'] is False
        assert response.data[0]['phases'][0]['name'] == 'Voting phase'
        assert response.data[0]['phases'][0]['is_active'] is False

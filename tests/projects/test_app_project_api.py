import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_app_project_api(project_factory, apiclient):
    project_1 = project_factory(is_app_accessible=True)
    project_2 = project_factory(is_app_accessible=True)
    project_3 = project_factory(is_app_accessible=True)
    project_4 = project_factory(is_app_accessible=False)
    project_5 = project_factory(is_app_accessible=True, is_draft=True)
    project_6 = project_factory(is_app_accessible=True, is_archived=True)

    url = reverse('app-projects-list')
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == project_1.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == project_2.pk)])
    assert any([True for dict in response.data
               if ('pk' in dict and dict['pk'] == project_3.pk)])
    assert not any([True for dict in response.data
                   if ('pk' in dict and dict['pk'] == project_4.pk)])
    assert not any([True for dict in response.data
                   if ('pk' in dict and dict['pk'] == project_5.pk)])
    assert not any([True for dict in response.data
                   if ('pk' in dict and dict['pk'] == project_6.pk)])


@pytest.mark.django_db
def test_app_project_api_single_agenda_setting_module(
        client, apiclient, project_factory):
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

    url = reverse('app-projects-list')
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert response.data[0]['single_agenda_setting_module'] \
        == module.pk
    assert response.data[0]['single_poll_module'] is False


@pytest.mark.django_db
def test_app_project_api_single_poll_module(
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

    url = reverse('app-projects-list')
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert response.data[0]['single_agenda_setting_module'] is False
    assert response.data[0]['single_poll_module'] \
        == module.pk


@pytest.mark.django_db
def test_app_project_serializer(project_factory, module_factory, apiclient):
    project = project_factory(
        is_app_accessible=True,
        information='<p>information with a <strong>bold</strong> bit</p>',
        result='result without any tags'
    )
    module = module_factory(project=project)
    module_factory(project=project, is_draft=True)

    url = reverse('app-projects-list')
    response = apiclient.get(url, format='json')

    assert response.status_code == 200
    assert response.data[0]['information'] == 'information with a bold bit'
    assert response.data[0]['result'] == 'result without any tags'
    assert response.data[0]['published_modules'] == [module.pk]
    assert response.data[0]['organisation'] == project.organisation.name
    assert response.data[0]['access'] == 'PUBLIC'
    assert response.data[0]['single_agenda_setting_module'] is False
    assert response.data[0]['single_poll_module'] is False

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

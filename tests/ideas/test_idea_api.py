import pytest
from django.urls import reverse


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

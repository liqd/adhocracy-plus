import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from apps.classifications.models import UserClassification


@pytest.mark.django_db
def test_report_on_comment_triggers_user_classification(user,
                                                        apiclient,
                                                        comment_factory,
                                                        idea_factory):
    idea = idea_factory()
    comment = comment_factory(content_object=idea)
    apiclient.force_authenticate(user=user)
    url = reverse('reports-list')
    comment_ct = ContentType.objects.get_for_model(comment)
    data = {
        'content_type': comment_ct.pk,
        'object_pk': comment.pk,
        'description': 'This comment sucks'
    }
    response = apiclient.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert len(UserClassification.objects.all()) == 1
    assert UserClassification.objects.first().comment == comment


@pytest.mark.django_db
def test_report_on_idea_does_not_trigger_user_classification(user,
                                                             apiclient,
                                                             idea_factory):
    idea = idea_factory()
    apiclient.force_authenticate(user=user)
    url = reverse('reports-list')
    idea_ct = ContentType.objects.get_for_model(idea)
    data = {
        'content_type': idea_ct.pk,
        'object_pk': idea.pk,
        'description': 'This comment sucks'
    }
    response = apiclient.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert len(UserClassification.objects.all()) == 0

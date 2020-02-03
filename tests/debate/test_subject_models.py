import pytest
from django.urls import reverse

from adhocracy4.comments import models as comments_models
from apps.debate.models import Subject


@pytest.mark.django_db
def test_absolute_url(subject):
    url = reverse(
        'a4_candy_debate:subject-detail',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': '{:05d}'.format(subject.pk),
            'year': subject.created.year
        })
    assert subject.get_absolute_url() == url


@pytest.mark.django_db
def test_str(subject):
    subject_string = subject.__str__()
    assert subject_string == subject.name


@pytest.mark.django_db
def test_project(subject):
    assert subject.module.project == subject.project


@pytest.mark.django_db
def test_reference_number(subject):
    reference_number = '{:d}-{:05d}'.format(subject.created.year, subject.pk)
    assert subject.reference_number == reference_number


@pytest.mark.django_db
def test_delete_subject(subject_factory, comment_factory, rating_factory):
    subject = subject_factory()

    for i in range(5):
        comment_factory(content_object=subject)
    comment_count = comments_models.Comment.objects.all().count()
    assert comment_count == len(subject.comments.all())

    count = Subject.objects.all().count()
    assert count == 1
    assert comment_count == 5

    subject.delete()
    count = Subject.objects.all().count()
    comment_count = comments_models.Comment.objects.all().count()
    assert count == 0
    assert comment_count == 0


@pytest.mark.django_db
def test_comment_creator_count(subject_factory, comment_factory,
                               user_factory):
    subject1 = subject_factory()
    subject2 = subject_factory()
    subject3 = subject_factory()

    user1 = user_factory()
    user2 = user_factory()
    user3 = user_factory()
    user4 = user_factory()
    user5 = user_factory()

    comment_factory(content_object=subject1, creator=user1)
    comment_factory(content_object=subject1, creator=user1)
    comment_factory(content_object=subject1, creator=user2)
    comment_factory(content_object=subject1, creator=user2)
    comment_factory(content_object=subject1, creator=user3)
    comment_factory(content_object=subject1, creator=user4)
    comment_factory(content_object=subject1, creator=user5)

    comment_factory(content_object=subject2, creator=user1)
    comment_factory(content_object=subject2, creator=user1)
    comment_factory(content_object=subject2, creator=user2)
    comment_factory(content_object=subject2, creator=user2)
    comment_factory(content_object=subject2, creator=user3)

    assert subject1.comment_creator_count == 5
    assert subject2.comment_creator_count == 3
    assert subject3.comment_creator_count == 0


@pytest.mark.django_db
def test_comment_creator_count_minus_three(subject_factory, comment_factory,
                                           user_factory):
    subject1 = subject_factory()
    subject2 = subject_factory()
    subject3 = subject_factory()

    user1 = user_factory()
    user2 = user_factory()
    user3 = user_factory()
    user4 = user_factory()
    user5 = user_factory()

    comment_factory(content_object=subject1, creator=user1)
    comment_factory(content_object=subject1, creator=user1)
    comment_factory(content_object=subject1, creator=user2)
    comment_factory(content_object=subject1, creator=user2)
    comment_factory(content_object=subject1, creator=user3)
    comment_factory(content_object=subject1, creator=user4)
    comment_factory(content_object=subject1, creator=user5)

    comment_factory(content_object=subject2, creator=user1)
    comment_factory(content_object=subject2, creator=user1)
    comment_factory(content_object=subject2, creator=user2)
    comment_factory(content_object=subject2, creator=user2)
    comment_factory(content_object=subject2, creator=user3)

    assert subject1.comment_creator_count_minus_three == 2
    assert subject2.comment_creator_count_minus_three is None
    assert subject3.comment_creator_count_minus_three is None


@pytest.mark.django_db
def test_last_three_creators(subject_factory, comment_factory,
                             user_factory):
    subject1 = subject_factory()
    subject2 = subject_factory()
    subject3 = subject_factory()

    user1 = user_factory()
    user2 = user_factory()
    user3 = user_factory()
    user4 = user_factory()
    user5 = user_factory()

    comment_factory(content_object=subject1, creator=user1)
    comment_factory(content_object=subject1, creator=user1)
    comment_factory(content_object=subject1, creator=user2)
    comment_factory(content_object=subject1, creator=user2)
    comment_factory(content_object=subject1, creator=user3)
    comment_factory(content_object=subject1, creator=user4)
    comment_factory(content_object=subject1, creator=user5)

    comment_factory(content_object=subject2, creator=user1)
    comment_factory(content_object=subject2, creator=user1)
    comment_factory(content_object=subject2, creator=user2)
    comment_factory(content_object=subject2, creator=user2)
    comment_factory(content_object=subject2, creator=user3)

    assert user3 in subject1.last_three_creators
    assert user4 in subject1.last_three_creators
    assert user5 in subject1.last_three_creators
    assert user1 in subject2.last_three_creators
    assert user2 in subject2.last_three_creators
    assert user3 in subject2.last_three_creators
    assert len(subject3.last_three_creators) == 0

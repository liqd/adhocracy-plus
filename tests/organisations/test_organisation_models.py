import os

import pytest
from dateutil.parser import parse
from django.conf import settings
from django.urls import reverse
from freezegun import freeze_time

from adhocracy4.projects.enums import Access
from apps.organisations import models
from tests import helpers


@pytest.mark.django_db
def test_absolute_url(organisation):
    url = reverse('organisation', kwargs={
        'organisation_slug': organisation.slug
    })
    assert organisation.get_absolute_url() == url


@pytest.mark.django_db
def test_string_representation(organisation):
    assert str(organisation) == organisation.name


@pytest.mark.django_db
def test_image_validation_image_too_small(organisation_factory, smallImage):
    organisation = organisation_factory(image=smallImage, logo=smallImage)
    with pytest.raises(Exception) as e:
        organisation.full_clean()
    assert 'Image must be at least 500 pixels high' in str(e.value)


@pytest.mark.django_db
def test_image_big_enough(organisation_factory, bigImage):
    organisation = organisation_factory(image=bigImage, logo=bigImage)
    assert organisation.full_clean() is None


@pytest.mark.django_db
def test_image_validation_type_not_allowed(organisation_factory, ImageBMP):
    organisation = organisation_factory(image=ImageBMP, logo=ImageBMP)
    with pytest.raises(Exception) as e:
        organisation.full_clean()
    assert 'Unsupported file format.' in str(e.value)


@pytest.mark.django_db
def test_image_validation_image_type_allowed(organisation_factory, ImagePNG):
    organisation = organisation_factory(image=ImagePNG, logo=ImagePNG)
    assert organisation.full_clean() is None


@pytest.mark.django_db
def test_delete_organisation(organisation_factory, ImagePNG):
    organisation = organisation_factory(image=ImagePNG, logo=ImagePNG)
    image_path = os.path.join(settings.MEDIA_ROOT, organisation.image.path)
    logo_path = os.path.join(settings.MEDIA_ROOT, organisation.logo.path)
    thumbnail_image_path = helpers.createThumbnail(organisation.image)
    thumbnail_logo_path = helpers.createThumbnail(organisation.logo)

    assert os.path.isfile(thumbnail_image_path)
    assert os.path.isfile(thumbnail_logo_path)
    assert os.path.isfile(image_path)
    assert os.path.isfile(logo_path)
    count = models.Organisation.objects.all().count()
    assert count == 1

    organisation.delete()
    assert not os.path.isfile(thumbnail_image_path)
    assert not os.path.isfile(thumbnail_logo_path)
    assert not os.path.isfile(image_path)
    assert not os.path.isfile(logo_path)
    count = models.Organisation.objects.all().count()
    assert count == 0


@pytest.mark.django_db
def test_image_deleted_after_update(organisation_factory, ImagePNG):
    organisation = organisation_factory(image=ImagePNG, logo=ImagePNG)
    image_path = os.path.join(settings.MEDIA_ROOT, organisation.image.path)
    logo_path = os.path.join(settings.MEDIA_ROOT, organisation.logo.path)
    thumbnail_image_path = helpers.createThumbnail(organisation.image)
    thumbnail_logo_path = helpers.createThumbnail(organisation.logo)

    assert os.path.isfile(thumbnail_image_path)
    assert os.path.isfile(thumbnail_logo_path)
    assert os.path.isfile(image_path)
    assert os.path.isfile(logo_path)

    new_image_path = os.path.join(
        settings.MEDIA_ROOT,
        os.path.dirname(organisation.image.path) + '/new.png'
    )
    os.rename(organisation.image.path, new_image_path)
    organisation.image = new_image_path
    organisation.logo = None
    organisation.save()

    assert os.path.isfile(new_image_path)
    assert not os.path.isfile(thumbnail_image_path)
    assert not os.path.isfile(thumbnail_logo_path)
    assert not os.path.isfile(image_path)
    assert not os.path.isfile(logo_path)


@pytest.mark.django_db
def test_social_share(organisation_factory):
    organisation_none = organisation_factory()
    organisation_facebook = organisation_factory(facebook_handle='my_facebook')
    organisation_twitter = organisation_factory(twitter_handle='my_twitter')
    organisation_instagram = organisation_factory(
        instagram_handle='my_instagram'
    )

    assert not organisation_none.has_social_share()
    assert organisation_facebook.has_social_share()
    assert organisation_twitter.has_social_share()
    assert organisation_instagram.has_social_share()


@pytest.mark.django_db
def test_has_initiator(organisation, user):
    initiator = organisation.initiators.first()

    assert organisation.has_initiator(initiator)
    assert not organisation.has_initiator(user)


@pytest.mark.django_db
def test_has_org_member(member, user_factory):
    organisation = member.organisation
    member = member.member
    user = user_factory()

    assert user != member
    assert organisation.has_org_member(member)
    assert not organisation.has_org_member(user)


@pytest.mark.django_db
def test_get_projects_list(module_factory, organisation, phase_factory,
                           project_factory, admin, user):
    pro1 = project_factory(organisation=organisation)
    pro2 = project_factory(organisation=organisation)
    pro3 = project_factory(access=Access.PRIVATE, organisation=organisation)
    pro4 = project_factory(access=Access.PRIVATE, organisation=organisation)
    pro5 = project_factory(organisation=organisation)

    module1 = module_factory(project=pro1)
    module2 = module_factory(project=pro2)
    module3 = module_factory(project=pro3)
    module4 = module_factory(project=pro4)
    module5 = module_factory(project=pro5)
    module6 = module_factory(project=pro5)

    phase_factory(
        module=module1,
        start_date=parse('2013-01-01 17:10:00 UTC'),
        end_date=parse('2013-01-01 19:05:00 UTC'),
    )

    phase_factory(
        module=module2,
        start_date=parse('2013-01-01 19:05:00 UTC'),
        end_date=parse('2013-01-01 20:00:00 UTC')
    )

    phase_factory(
        module=module3,
        start_date=parse('2013-01-01 17:50:00 UTC'),
        end_date=parse('2013-01-01 20:00:00 UTC')
    )

    phase_factory(
        module=module4,
        start_date=parse('2013-01-01 14:50:00 UTC'),
        end_date=parse('2013-01-01 17:00:00 UTC')
    )

    phase_factory(
        module=module5,
        start_date=parse('2013-01-01 17:10:00 UTC'),
        end_date=parse('2013-01-01 17:30:00 UTC'),
    )

    phase_factory(
        module=module6,
        start_date=parse('2013-01-01 18:10:00 UTC'),
        end_date=parse('2013-01-01 19:05:00 UTC'),
    )

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        projects_list = organisation.get_projects_list(user)
        active_projects = projects_list[0]
        future_projects = projects_list[1]
        past_projects = projects_list[2]

        assert projects_list
        assert len(active_projects) == 2
        assert len(future_projects) == 1
        assert not past_projects

        projects_list = organisation.get_projects_list(admin)
        active_projects = projects_list[0]
        future_projects = projects_list[1]
        past_projects = projects_list[2]

        assert projects_list
        assert len(active_projects) == 3
        assert len(future_projects) == 1
        assert len(past_projects) == 1

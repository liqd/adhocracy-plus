import os

import pytest
from dateutil.parser import parse
from django.conf import settings
from django.urls import reverse
from freezegun import freeze_time

from adhocracy4.projects.enums import Access
from adhocracy4.test.helpers import create_thumbnail
from apps.organisations import models


@pytest.mark.django_db
def test_absolute_url(organisation):
    url = reverse("organisation", kwargs={"organisation_slug": organisation.slug})
    assert organisation.get_absolute_url() == url


@pytest.mark.django_db
def test_string_representation(organisation):
    assert str(organisation) == organisation.name


@pytest.mark.django_db
def test_image_validation_image_too_small(organisation_factory, small_image):
    organisation = organisation_factory(image=small_image, logo=small_image)
    with pytest.raises(Exception) as e:
        organisation.full_clean()
    assert "Image must be at least 500 pixels high" in str(e.value)


@pytest.mark.django_db
def test_image_big_enough(organisation_factory, big_image, small_image):
    organisation = organisation_factory(image=big_image, logo=small_image)
    assert organisation.full_clean() is None


@pytest.mark.django_db
def test_image_validation_logo_too_big(organisation_factory, big_image):
    organisation = organisation_factory(logo=big_image)
    with pytest.raises(Exception) as e:
        organisation.full_clean()
    assert "Image must be at most 800 pixels high" in str(e.value)


@pytest.mark.django_db
def test_image_validation_type_not_allowed(organisation_factory, image_bmp):
    organisation = organisation_factory(image=image_bmp, logo=image_bmp)
    with pytest.raises(Exception) as e:
        organisation.full_clean()
    assert "Unsupported file format." in str(e.value)


@pytest.mark.django_db
def test_image_validation_image_type_allowed(organisation_factory, image_png):
    organisation = organisation_factory(image=image_png)
    assert organisation.full_clean() is None


@pytest.mark.django_db
def test_delete_organisation(organisation_factory, image_png):
    organisation = organisation_factory(image=image_png, logo=image_png)
    image_path = os.path.join(settings.MEDIA_ROOT, organisation.image.path)
    logo_path = os.path.join(settings.MEDIA_ROOT, organisation.logo.path)
    thumbnail_image_path = create_thumbnail(organisation.image)
    thumbnail_logo_path = create_thumbnail(organisation.logo)

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
def test_image_deleted_after_update(organisation_factory, image_png):
    organisation = organisation_factory(image=image_png, logo=image_png)
    image_path = os.path.join(settings.MEDIA_ROOT, organisation.image.path)
    logo_path = os.path.join(settings.MEDIA_ROOT, organisation.logo.path)
    thumbnail_image_path = create_thumbnail(organisation.image)
    thumbnail_logo_path = create_thumbnail(organisation.logo)

    assert os.path.isfile(thumbnail_image_path)
    assert os.path.isfile(thumbnail_logo_path)
    assert os.path.isfile(image_path)
    assert os.path.isfile(logo_path)

    new_image_path = os.path.join(
        settings.MEDIA_ROOT, os.path.dirname(organisation.image.path) + "/new.png"
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
    organisation_facebook = organisation_factory(facebook_handle="my_facebook")
    organisation_twitter = organisation_factory(twitter_handle="my_twitter")
    organisation_instagram = organisation_factory(instagram_handle="my_instagram")

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
def test_get_projects_list(
    module_factory, organisation, phase_factory, project_factory, admin, user
):
    project_active1 = project_factory(organisation=organisation)
    project_active2 = project_factory(organisation=organisation)
    project_future1 = project_factory(organisation=organisation)
    project_future2 = project_factory(access=Access.PRIVATE, organisation=organisation)
    project_past1 = project_factory(access=Access.PRIVATE, organisation=organisation)
    project_past2 = project_factory(organisation=organisation)

    phase_factory(
        module__project=project_active1,
        start_date=parse("2013-01-01 17:10:00 UTC"),
        end_date=parse("2013-01-01 19:05:00 UTC"),
    )

    phase_factory(
        module__project=project_active2,
        start_date=parse("2013-01-01 17:50:00 UTC"),
        end_date=parse("2013-01-01 20:00:00 UTC"),
    )

    phase_factory(
        module__project=project_future1,
        start_date=parse("2013-01-01 19:05:00 UTC"),
        end_date=parse("2013-01-01 20:00:00 UTC"),
    )

    phase_factory(
        module__project=project_future2,
        start_date=parse("2013-01-01 19:25:00 UTC"),
        end_date=parse("2013-01-01 20:15:00 UTC"),
    )

    phase_factory(
        module__project=project_past1,
        start_date=parse("2013-01-01 14:50:00 UTC"),
        end_date=parse("2013-01-01 17:00:00 UTC"),
    )

    phase_factory(
        module__project=project_past2,
        start_date=parse("2013-01-01 17:10:00 UTC"),
        end_date=parse("2013-01-01 17:30:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        projects_list = organisation.get_projects_list(user)
        active_projects = projects_list[0]
        future_projects = projects_list[1]
        past_projects = projects_list[2]

        assert projects_list
        assert len(active_projects) == 2
        # assert sorting: earliest end date -> latest end date
        assert active_projects[0] == project_active1
        assert active_projects[1] == project_active2
        assert len(future_projects) == 1
        assert len(past_projects) == 1

        projects_list = organisation.get_projects_list(admin)
        active_projects = projects_list[0]
        future_projects = projects_list[1]
        past_projects = projects_list[2]

        assert projects_list
        assert len(active_projects) == 2
        # assert sorting: earliest end date -> latest end date
        assert active_projects[0] == project_active1
        assert active_projects[1] == project_active2

        assert len(future_projects) == 2
        # assert sorting: earliest start date -> latest start date
        assert future_projects[0] == project_future1
        assert future_projects[1] == project_future2

        assert len(past_projects) == 2
        # assert sorting: latest end date ->  earliest end date
        assert past_projects[0] == project_past2
        assert past_projects[1] == project_past1

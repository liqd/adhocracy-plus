import json

import pytest
from dateutil.parser import parse
from django.contrib.auth.models import AnonymousUser
from django.template import Context
from django.test import RequestFactory
from freezegun import freeze_time

from adhocracy4.follows.models import Follow
from apps.projects.templatetags import a4_candy_project_tags as tags
from tests.helpers import GuestUserCreator


@pytest.mark.django_db
def test_project_participation_status_running(project, module_factory, phase_factory):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        status = tags.project_participation_status(project)
    assert status == {"label": "running", "modifier": "running"}


@pytest.mark.django_db
def test_project_participation_status_upcoming(project, module_factory, phase_factory):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-02-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        status = tags.project_participation_status(project)
    assert status == {"label": "upcoming", "modifier": "upcoming"}


@pytest.mark.django_db
def test_project_participation_status_completed(project, module_factory, phase_factory):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 18:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-02 18:00:00 UTC")):
        status = tags.project_participation_status(project)
    assert status == {"label": "completed", "modifier": "completed"}


@pytest.mark.django_db
def test_get_project_follower_count(project, follow_factory, user_factory):
    Follow.objects.filter(project=project).delete()
    follow_factory(project=project, creator=user_factory(), enabled=True)
    follow_factory(project=project, creator=user_factory(), enabled=True)
    follow_factory(project=project, creator=user_factory(), enabled=False)
    assert tags.get_project_follower_count(project) == 2


@pytest.mark.django_db
def test_get_project_followers(project, follow_factory, user_factory):
    Follow.objects.filter(project=project).delete()
    user1 = user_factory()
    user2 = user_factory()
    follow_factory(project=project, creator=user1, enabled=True)
    follow_factory(project=project, creator=user2, enabled=True)
    follow_factory(project=project, creator=user_factory(), enabled=False)
    followers = tags.get_project_followers(project, limit=4)
    assert len(followers) == 2
    assert user1 in followers
    assert user2 in followers


@pytest.mark.django_db
def test_get_project_followers_respects_limit(project, follow_factory, user_factory):
    Follow.objects.filter(project=project).delete()
    for _ in range(5):
        follow_factory(project=project, creator=user_factory(), enabled=True)
    assert len(tags.get_project_followers(project, limit=3)) == 3


@pytest.mark.django_db
def test_get_project_follower_count_excludes_guest_users(
    project, follow_factory, user_factory
):
    Follow.objects.filter(project=project).delete()
    guest_user = GuestUserCreator().create_guest_user()
    follow_factory(project=project, creator=guest_user, enabled=True)
    follow_factory(project=project, creator=user_factory(), enabled=True)
    assert tags.get_project_follower_count(project) == 1


@pytest.mark.django_db
def test_get_project_followers_excludes_guest_users(
    project, follow_factory, user_factory
):
    Follow.objects.filter(project=project).delete()
    guest_user = GuestUserCreator().create_guest_user()
    registered_user = user_factory()
    follow_factory(project=project, creator=guest_user, enabled=True)
    follow_factory(project=project, creator=registered_user, enabled=True)
    followers = tags.get_project_followers(project, limit=4)
    assert len(followers) == 1
    assert registered_user in followers
    assert guest_user not in followers


@pytest.mark.django_db
def test_project_detail_follow_widget_attrs_anonymous(project):
    Follow.objects.filter(project=project).delete()
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    context = Context({"request": request})
    attrs = json.loads(tags.project_detail_follow_widget_attrs(context, project))
    assert attrs["project"] == project.slug
    assert "authenticatedAs" not in attrs
    assert "user" not in attrs
    assert attrs["initialFollowers"] == []
    assert attrs["initialFollowerCount"] == 0


@pytest.mark.django_db
def test_project_detail_follow_widget_attrs_authenticated(
    project, user, follow_factory, user_factory
):
    Follow.objects.filter(project=project).delete()
    other = user_factory()
    follow_factory(project=project, creator=other, enabled=True)
    follow_factory(project=project, creator=user_factory(), enabled=False)

    request = RequestFactory().get("/")
    request.user = user
    context = Context({"request": request})
    attrs = json.loads(tags.project_detail_follow_widget_attrs(context, project))

    assert attrs["authenticatedAs"] == user.username
    assert attrs["user"]["pk"] == user.pk
    assert attrs["initialFollowerCount"] == 1
    assert len(attrs["initialFollowers"]) == 1
    assert attrs["initialFollowers"][0]["pk"] == other.pk
    assert "avatarFallback" in attrs["initialFollowers"][0]
    assert "avatarFallback" in attrs["user"]

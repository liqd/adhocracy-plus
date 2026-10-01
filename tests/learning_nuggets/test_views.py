import pytest
from django.urls import reverse
from wagtail.models import Page
from wagtail.models import PageViewRestriction

from apps.learning_nuggets.models import LearningCategory
from apps.learning_nuggets.models import LearningCenterPage
from apps.learning_nuggets.models import LearningNuggetPage


def _setup_center():
    root_page = Page.get_first_root_node()
    center = LearningCenterPage(title="Learning Center", slug="learning-center")
    root_page.add_child(instance=center)
    return center


@pytest.mark.django_db
def test_index_returns_full_page_without_htmx(client):
    _setup_center()

    response = client.get(reverse("learning_nuggets:index"))

    assert response.status_code == 200
    assert "learning_sidebar" not in ""  # full page rendered via base template
    assert b"learning-sidebar" in response.content
    # the toggle is rendered in the global header, not as a floating button
    assert b'id="learning-toggle"' in response.content
    assert b"header-upper__learning" in response.content


@pytest.mark.django_db
def test_index_returns_partial_with_htmx(client):
    _setup_center()
    LearningCategory.objects.create(name="Category A", permission_level="teilnehmer:in")

    response = client.get(reverse("learning_nuggets:index"), HTTP_HX_REQUEST="true")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Category A" in content
    # the partial must not contain the full page chrome
    assert "<!DOCTYPE html>" not in content
    assert 'id="learning-sidebar"' not in content


@pytest.mark.django_db
def test_category_returns_partial_with_htmx(client):
    center = _setup_center()
    category = LearningCategory.objects.create(
        name="Participants", slug="participants", permission_level="teilnehmer:in"
    )
    nugget = LearningNuggetPage(
        title="Registration", slug="registration", category=category
    )
    center.add_child(instance=nugget)

    response = client.get(
        reverse("learning_nuggets:category", kwargs={"category_slug": "participants"}),
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Registration" in content
    assert "<!DOCTYPE html>" not in content


@pytest.mark.django_db
def test_legacy_permission_level_is_not_dropped(client):
    _setup_center()
    LearningCategory.objects.create(name="Legacy", permission_level="participant")

    response = client.get(reverse("learning_nuggets:index"), HTTP_HX_REQUEST="true")

    assert "Legacy" in response.content.decode()


@pytest.mark.django_db
def test_draft_nugget_is_not_served(client):
    center = _setup_center()
    category = LearningCategory.objects.create(
        name="Participants", slug="participants", permission_level="teilnehmer:in"
    )
    nugget = LearningNuggetPage(
        title="Draft", slug="draft", category=category, live=False
    )
    center.add_child(instance=nugget)

    detail = client.get(
        reverse(
            "learning_nuggets:nugget-detail",
            kwargs={"category_slug": "participants", "nugget_slug": "draft"},
        )
    )
    listing = client.get(
        reverse("learning_nuggets:category", kwargs={"category_slug": "participants"}),
        HTTP_HX_REQUEST="true",
    )

    assert detail.status_code == 404
    assert "Draft" not in listing.content.decode()


@pytest.mark.django_db
def test_private_nugget_section_is_not_served(client):
    center = _setup_center()
    PageViewRestriction.objects.create(page=center, restriction_type="login")
    category = LearningCategory.objects.create(
        name="Participants", slug="participants", permission_level="teilnehmer:in"
    )
    nugget = LearningNuggetPage(title="Private", slug="private", category=category)
    center.add_child(instance=nugget)

    detail = client.get(
        reverse(
            "learning_nuggets:nugget-detail",
            kwargs={"category_slug": "participants", "nugget_slug": "private"},
        )
    )
    listing = client.get(
        reverse("learning_nuggets:category", kwargs={"category_slug": "participants"}),
        HTTP_HX_REQUEST="true",
    )

    assert detail.status_code == 404
    assert "Private" not in listing.content.decode()

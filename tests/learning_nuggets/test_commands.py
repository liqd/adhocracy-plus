import pytest
from django.core.management import call_command
from django.urls import reverse
from wagtail.models import Page

from apps.learning_nuggets.models import LearningCategory
from apps.learning_nuggets.models import LearningCenterPage
from apps.learning_nuggets.models import LearningNuggetPage


@pytest.fixture
def homepage():
    root_page = Page.get_first_root_node()
    home = root_page.get_children().first()
    if home is None:
        home = Page(title="Home", slug="home")
        root_page.add_child(instance=home)
    return home


def _demo_pages():
    return LearningNuggetPage.objects.filter(slug__startswith="demo-")


@pytest.mark.django_db
def test_seed_creates_demo_data(homepage):
    call_command("seed_learning_nuggets", verbosity=0)

    center = LearningCenterPage.objects.get()
    assert center.live
    assert LearningCategory.objects.filter(slug__startswith="demo-").count() == 5
    assert _demo_pages().count() == 8
    assert _demo_pages().filter(live=True).count() == 7
    assert _demo_pages().filter(slug="demo-entwurf-passwort", live=False).exists()


@pytest.mark.django_db
def test_seed_is_idempotent(homepage):
    call_command("seed_learning_nuggets", verbosity=0)
    first_ids = set(_demo_pages().values_list("pk", flat=True))

    call_command("seed_learning_nuggets", verbosity=0)

    assert set(_demo_pages().values_list("pk", flat=True)) == first_ids
    assert _demo_pages().count() == 8
    assert LearningCategory.objects.filter(slug__startswith="demo-").count() == 5


@pytest.mark.django_db
def test_reset_recreates_demo_data(homepage):
    call_command("seed_learning_nuggets", verbosity=0)
    first_ids = set(_demo_pages().values_list("pk", flat=True))

    call_command("seed_learning_nuggets", reset=True, verbosity=0)
    second_ids = set(_demo_pages().values_list("pk", flat=True))

    assert first_ids.isdisjoint(second_ids)
    assert len(second_ids) == 8


@pytest.mark.django_db
def test_seeded_data_is_searchable(client, homepage):
    call_command("seed_learning_nuggets", verbosity=0)

    response = client.get(
        reverse("learning_nuggets:index"),
        {"q": "passwort"},
        HTTP_HX_REQUEST="true",
    )
    content = response.content.decode()

    assert "Konto verwalten" in content
    assert "Entwurf: Passwort-Reset" not in content

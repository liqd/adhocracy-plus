import pytest
from django.urls import reverse
from wagtail.models import Page
from wagtail.models import PageViewRestriction

from apps.learning_nuggets.models import LearningCategory
from apps.learning_nuggets.models import LearningCenterPage
from apps.learning_nuggets.models import LearningNuggetPage
from apps.learning_nuggets.views import matches_text


def _setup_center():
    root_page = Page.get_first_root_node()
    center = LearningCenterPage(title="Learning Center", slug="learning-center")
    root_page.add_child(instance=center)
    return center


def _add_nugget(center, category, title, slug, blocks=None, live=True):
    nugget = LearningNuggetPage(
        title=title,
        slug=slug,
        category=category,
        live=live,
        content=[("learning_nugget", block) for block in blocks or []],
    )
    center.add_child(instance=nugget)
    return nugget


@pytest.mark.django_db
def test_index_returns_full_page_without_htmx(client):
    _setup_center()

    response = client.get(reverse("learning_nuggets:index"))

    assert response.status_code == 200
    assert b'id="learning-sidebar"' in response.content
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
    assert listing.status_code == 404
    assert "Private" not in listing.content.decode()


@pytest.mark.django_db
def test_private_center_is_not_served(client):
    center = _setup_center()
    PageViewRestriction.objects.create(page=center, restriction_type="login")

    partial = client.get(reverse("learning_nuggets:index"), HTTP_HX_REQUEST="true")
    full_page = client.get(reverse("learning_nuggets:index"))

    assert partial.status_code == 404
    assert full_page.status_code == 404


def _search(client, query):
    return client.get(
        reverse("learning_nuggets:index"),
        {"q": query},
        HTTP_HX_REQUEST="true",
    )


@pytest.mark.parametrize(
    "text, query, expected",
    [
        ("Profil einrichten", "Profile", True),
        ("Profile verwalten", "Profil", True),
        ("Projekt anlegen", "Projekte", True),
        ("Konto verwalten", "Konten", True),
        ("Idee einreichen", "Ideen", True),
        ("Ideen einreichen", "Idee", True),
        ("Passwort zurücksetzen", "Passwörter", True),
        ("Häuser verwalten", "Haus", True),
        ("Registration", "regist", True),
        ("Haus", "Haut", False),
        ("Profil", "xyz", False),
    ],
)
def test_matches_text_handles_german_plurals(text, query, expected):
    assert matches_text(text, query) is expected


@pytest.mark.django_db
def test_search_matches_german_plural_query(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Profil einrichten",
        "profil-einrichten",
        [{"title": "Profil anlegen", "description": "<p>Profil bearbeiten</p>"}],
    )
    _add_nugget(
        center,
        category,
        "Konto verwalten",
        "konto-verwalten",
        [{"title": "Passwort zurücksetzen", "description": "<p>Hilfe</p>"}],
    )

    content = _search(client, "Profile").content.decode()
    assert "Profil einrichten" in content

    content = _search(client, "Passwörter").content.decode()
    assert "Konto verwalten" in content


@pytest.mark.django_db
def test_sidebar_contains_search_form(client):
    _setup_center()

    content = client.get(reverse("learning_nuggets:index")).content.decode()

    assert 'id="learning-search-input"' in content
    assert 'id="learning-search-status"' in content
    assert 'aria-live="polite"' in content


@pytest.mark.django_db
def test_full_page_search_echoes_query(client):
    _setup_center()

    content = client.get(
        reverse("learning_nuggets:index"), {"q": "profil"}
    ).content.decode()

    assert 'value="profil"' in content


@pytest.mark.django_db
def test_search_uses_plural_summary(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(center, category, "Profile", "profile")
    _add_nugget(center, category, "Delete profile", "delete-profile")

    content = _search(client, "profile").content.decode()

    assert "2 results for" in content


@pytest.mark.django_db
def test_search_updates_live_region(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(center, category, "Registration", "registration")

    content = _search(client, "registration").content.decode()

    assert 'hx-swap-oob="innerHTML:#learning-search-status"' in content
    assert "1 result for" in content
    assert "<!DOCTYPE html>" not in content


@pytest.mark.django_db
def test_search_escapes_the_query(client):
    _setup_center()

    content = _search(client, "<script>").content.decode()

    assert "<script>" not in content
    assert "&lt;script&gt;" in content


@pytest.mark.django_db
def test_search_matches_page_title_case_insensitively(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Registration",
        "sign-up",
        [{"title": "Sign up", "description": "<p>Some description</p>"}],
    )

    response = _search(client, "REGIST")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Registration" in content
    assert "No results for" not in content


@pytest.mark.django_db
def test_search_matches_nugget_title(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Getting Started",
        "getting-started",
        [{"title": "Registration", "description": "<p>Something else</p>"}],
    )

    response = _search(client, "regist")

    assert "Getting Started" in response.content.decode()


@pytest.mark.django_db
def test_search_matches_nugget_description(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Getting Started",
        "getting-started",
        [{"title": "Intro", "description": "<p>How registration works</p>"}],
    )

    response = _search(client, "regist")

    assert "Getting Started" in response.content.decode()


@pytest.mark.django_db
def test_search_shows_only_page_titles(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Getting Started",
        "getting-started",
        [
            {
                "title": "Registration",
                "description": "<p>Secret description</p>",
            }
        ],
    )

    response = _search(client, "regist")
    content = response.content.decode()

    assert "Getting Started" in content
    assert "Registration" not in content
    assert "Secret description" not in content


@pytest.mark.django_db
def test_search_lists_a_page_only_once(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Profile",
        "profile",
        [
            {"title": "Set Up Your Profile", "description": "<p>Profile setup</p>"},
            {"title": "Delete Profile", "description": "<p>Profile removal</p>"},
        ],
    )

    response = _search(client, "profile")
    content = response.content.decode()

    assert content.count('class="learning-search-result"') == 1
    assert "1 result for" in content


@pytest.mark.django_db
def test_search_returns_no_results_message(client):
    _setup_center()

    response = _search(client, "does-not-exist")
    content = response.content.decode()

    assert "No results for" in content
    assert 'class="learning-search-result"' not in content


@pytest.mark.django_db
def test_search_with_empty_query_shows_index(client):
    _setup_center()
    LearningCategory.objects.create(name="Category A")

    response = _search(client, " ")

    assert "Category A" in response.content.decode()


@pytest.mark.django_db
def test_search_ignores_draft_and_private_nuggets(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(
        center,
        category,
        "Draft page",
        "draft-page",
        [{"title": "Registration"}],
        live=False,
    )

    assert "Draft page" not in _search(client, "registration").content.decode()

    _add_nugget(
        center,
        category,
        "Create account",
        "create-account",
        [{"title": "Registration"}],
    )

    assert "Create account" in _search(client, "registration").content.decode()

    PageViewRestriction.objects.create(page=center, restriction_type="login")

    assert "Create account" not in _search(client, "registration").content.decode()


@pytest.mark.django_db
def test_search_ignores_nuggets_without_category(client):
    center = _setup_center()
    _add_nugget(center, None, "Registration", "registration")

    assert "Registration" not in _search(client, "registration").content.decode()


@pytest.mark.django_db
def test_search_result_links_to_nugget_detail(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(center, category, "Registration", "registration")

    response = _search(client, "registration")
    content = response.content.decode()

    assert (
        reverse(
            "learning_nuggets:nugget-detail",
            kwargs={"category_slug": "participants", "nugget_slug": "registration"},
        )
        in content
    )


@pytest.mark.django_db
def test_search_full_page_without_htmx(client):
    center = _setup_center()
    category = LearningCategory.objects.create(name="Participants")
    _add_nugget(center, category, "Registration", "registration")

    response = client.get(reverse("learning_nuggets:index"), {"q": "registration"})
    content = response.content.decode()

    assert response.status_code == 200
    assert "<!DOCTYPE html>" in content
    assert "Registration" in content

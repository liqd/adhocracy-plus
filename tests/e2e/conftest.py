import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db import transaction
from django.urls import reverse
from wagtail.models import Locale
from wagtail.models import Page
from wagtail.models import Site as WagtailSite


@pytest.fixture(scope="session")
def base_url(live_server):
    """Route pytest-playwright against pytest-django's in-process server."""
    return live_server.url


@pytest.fixture(autouse=True)
def _e2e_database(transactional_db):
    """Ensure the test database is created/migrated for every e2e test.

    The live server runs in its own connection, so it needs the test database to
    be fully set up before any seeding or browsing happens.
    """
    yield


@pytest.fixture
def db_commit(django_db_blocker):
    """Run a callable against a dedicated, auto-committing DB connection.

    The live server runs on its own database connection, and pytest-django wraps
    each test in a rolled-back transaction via ``transactional_db``. Writes made
    on the default connection are invisible to the live server and are rolled
    back at the end of the test. Opening a dedicated connection with autocommit
    lets e2e tests persist seed data that the live server can see and that is not
    undone by the test's transaction.
    """

    def _commit(fn, *args, **kwargs):
        with django_db_blocker.unblock():
            connection = connections.create_connection("default")
            old_autocommit = connection.autocommit
            connection.autocommit = True
            try:
                with transaction.atomic(using="default"):
                    return fn(*args, **kwargs)
            finally:
                connection.autocommit = old_autocommit
                connection.close()

    return _commit


@pytest.fixture
def seed(django_db_blocker, db_commit):
    """Persist DB writes so the live server (separate connection) sees them.

    Created objects are written via a dedicated auto-committing connection and
    removed again on teardown so tests stay isolated from one another.
    """

    created = []

    def _seed(create, **kwargs):
        obj = db_commit(create, **kwargs)
        _collect(obj, created)
        return obj

    yield _seed

    def _cleanup():
        for obj in reversed(created):
            obj.delete()

    db_commit(_cleanup)


def _ensure_default_wagtail_site():
    """Recreate the default Wagtail site if a test removed it.

    Some app pages (login, landing) require a default Wagtail site whose
    root_page is cascade-deleted when test seed data is torn down. This mirrors
    Wagtail's initial-data migration so the site is always available.
    """
    if WagtailSite.objects.filter(is_default_site=True).exists():
        return

    page_content_type = ContentType.objects.get_for_model(Page)
    locale = Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)[0]
    root = Page.objects.create(
        title="Root",
        slug="root",
        content_type=page_content_type,
        path="0001",
        depth=1,
        numchild=1,
        url_path="/",
        locale=locale,
    )
    homepage = Page.objects.create(
        title="Home",
        slug="home",
        content_type=page_content_type,
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
        locale=locale,
    )
    WagtailSite.objects.create(
        hostname="localhost",
        port=80,
        root_page=homepage,
        is_default_site=True,
    )
    return root, homepage


@pytest.fixture(autouse=True)
def _ensure_default_site(db_commit):
    """Make the default Wagtail site available for each test.

    Seeding a project (idea create) can remove/repoint the default Wagtail site.
    Recreate it here, before the test renders any page, on a dedicated committing
    connection so it is visible to the live server.
    """
    db_commit(_ensure_default_wagtail_site)
    yield
    db_commit(_ensure_default_wagtail_site)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Allow the browser to launch as root inside CI containers."""
    return {**browser_type_launch_args, "args": ["--no-sandbox"]}


def _collect(obj, created):
    """Recursively collect django model instances for later cleanup."""
    if hasattr(obj, "_meta") and hasattr(obj, "delete"):
        created.append(obj)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _collect(item, created)
    elif isinstance(obj, dict):
        for value in obj.values():
            _collect(value, created)


@pytest.fixture
def e2e_login(page):
    """Log a Django user in through the real login page."""

    def login(user):
        page.goto(reverse("account_login"))
        page.locator('input[name="login"]').fill(user.email)
        page.locator('input[name="password"]').fill("password")
        page.get_by_role("button", name="Login").click()

    return login

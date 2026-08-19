import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Locale
from wagtail.models import Page
from wagtail.models import Site as WagtailSite

from adhocracy4.test.factories import PhaseFactory


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

    for obj in _dependency_order(created):
        if obj.pk is None:
            continue
        db_commit(obj.delete)


def _dependency_order(objs):
    """Order objects so children are deleted before their parents.

    Django's fast-delete collector can emit parent deletes before child deletes
    when a whole related graph cascades in one call (e.g. deleting a project
    that owns live questions with likes), which violates foreign keys on
    SQLite. Deleting each object on its own connection, leaf-first, avoids the
    issue entirely.
    """
    remaining = list(objs)
    result = []

    def _parents(obj):
        parents = set()
        for field in obj._meta.fields:
            if field.is_relation and field.many_to_one and not field.auto_created:
                try:
                    parents.add(getattr(obj, field.name))
                except ObjectDoesNotExist:
                    continue
        return parents

    while remaining:
        for obj in remaining:
            children = [o for o in remaining if obj in _parents(o)]
            if not children:
                result.append(obj)
                remaining.remove(obj)
                break

    return result + remaining


@pytest.fixture
def e2e_active_phase(seed):
    """Factory for seeding a module with an active phase.

    Call with a phase content instance, e.g. ``e2e_active_phase(IssuePhase())``.
    Returns a dict with phase, module and project, committed so the live server
    can see it and removed on teardown.
    """

    def _create(*, phase_content):
        now = timezone.now()
        phase = PhaseFactory(
            phase_content=phase_content,
            start_date=now - timezone.timedelta(days=1),
            end_date=now + timezone.timedelta(days=1),
        )
        return {
            "phase": phase,
            "module": phase.module,
            "project": phase.module.project,
        }

    return lambda phase_content: seed(_create, phase_content=phase_content)


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

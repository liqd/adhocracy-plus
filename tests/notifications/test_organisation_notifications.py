import pytest

from adhocracy4.dashboard import signals as a4_dashboard_signals
from apps.notifications.models import Notification
from apps.notifications.models import NotificationType
from apps.organisations.models import OrganisationFollow
from tests.helpers import GuestUserCreator
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_organisation_new_project_strategy_recipients(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    user = user_factory()
    OrganisationFollow.objects.create(
        organisation=organisation, creator=user, enabled=True
    )

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(sender=None, project=project, user=user)

    notifications = Notification.objects.filter(
        notification_type=NotificationType.ORGANISATION_NEW_PROJECT
    )
    assert notifications.count() == 1
    assert notifications.first().recipient == user


@pytest.mark.django_db
def test_organisation_new_project_strategy_ignores_non_followers(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    non_follower = user_factory()

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(
        sender=None, project=project, user=non_follower
    )

    notifications = Notification.objects.filter(
        notification_type=NotificationType.ORGANISATION_NEW_PROJECT
    )
    assert notifications.count() == 0


@pytest.mark.django_db
def test_organisation_new_project_strategy_ignores_disabled_follows(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    user = user_factory()
    OrganisationFollow.objects.create(
        organisation=organisation, creator=user, enabled=False
    )

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(sender=None, project=project, user=user)

    notifications = Notification.objects.filter(
        notification_type=NotificationType.ORGANISATION_NEW_PROJECT
    )
    assert notifications.count() == 0


@pytest.mark.django_db
def test_organisation_new_project_sends_email_to_followers(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    follower = user_factory()
    OrganisationFollow.objects.create(
        organisation=organisation, creator=follower, enabled=True
    )

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(
        sender=None, project=project, user=follower
    )

    follower_emails = get_emails_for_address(follower.email)
    assert len(follower_emails) == 1
    assert project.name.lower() in follower_emails[0].body.lower()
    assert organisation.name.lower() in follower_emails[0].body.lower()


@pytest.mark.django_db
def test_organisation_new_project_notification_type_and_context(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    follower = user_factory()
    OrganisationFollow.objects.create(
        organisation=organisation, creator=follower, enabled=True
    )

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(
        sender=None, project=project, user=follower
    )

    notification = Notification.objects.get(
        recipient=follower,
        notification_type=NotificationType.ORGANISATION_NEW_PROJECT,
    )
    assert notification.notification_type == NotificationType.ORGANISATION_NEW_PROJECT
    assert notification.target_url == project.get_absolute_url()
    assert project.name in notification.context["project"]
    assert organisation.name in notification.context["organisation"]


@pytest.mark.django_db
def test_organisation_new_project_excludes_guest_followers(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    guest_user = GuestUserCreator().create_guest_user()
    OrganisationFollow.objects.create(
        organisation=organisation, creator=guest_user, enabled=True
    )

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(
        sender=None, project=project, user=guest_user
    )

    notifications = Notification.objects.filter(
        notification_type=NotificationType.ORGANISATION_NEW_PROJECT
    )
    assert notifications.count() == 0
    assert len(get_emails_for_address(guest_user.email)) == 0


@pytest.mark.django_db
def test_organisation_new_project_respects_notification_settings(
    organisation_factory, project_factory, user_factory, module_factory, phase_factory
):
    organisation = organisation_factory()
    follower = user_factory()
    OrganisationFollow.objects.create(
        organisation=organisation, creator=follower, enabled=True
    )

    settings = follower.notification_settings
    settings.email_project_updates = False
    settings.notify_project_updates = False
    settings.save()

    project = project_factory(organisation=organisation, is_draft=False)
    module = module_factory(project=project)
    _setup_module_phase(module, phase_factory)

    a4_dashboard_signals.project_published.send(
        sender=None, project=project, user=follower
    )

    notifications = Notification.objects.filter(
        notification_type=NotificationType.ORGANISATION_NEW_PROJECT
    )
    assert notifications.count() == 0
    assert len(get_emails_for_address(follower.email)) == 0


def _setup_module_phase(module, phase_factory):
    from datetime import timedelta

    from django.utils import timezone

    phase_factory(
        module=module,
        start_date=timezone.now() - timedelta(days=1),
        end_date=timezone.now() + timedelta(days=30),
    )

import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import freeze_post_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import models
from apps.budgeting import phases


@pytest.mark.django_db
def test_create_view(
    client,
    phase_factory,
    proposal_factory,
    user,
    category_factory,
    area_settings_factory,
):
    phase, module, project, item = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        response = client.get(url)
        assert_template_response(
            response, "a4_candy_budgeting/proposal_create_form.html"
        )

        data = {
            "name": "Proposal",
            "description": "description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "proposal-detail"


@pytest.mark.django_db
def test_anonymous_cannot_create_proposal(client, phase_factory):
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Proposal.objects.all().count()
        assert count == 0
        response = client.get(url)
        assert response.status_code == 302
        assert redirect_target(response) == "account_login"


@pytest.mark.django_db
def test_user_can_create_proposal_during_active_phase(
    client, phase_factory, user, category_factory, area_settings_factory
):
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Proposal.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert_template_response(
            response, "a4_candy_budgeting/proposal_create_form.html"
        )
        assert response.status_code == 200
        proposal = {
            "name": "Proposal",
            "description": "description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, proposal)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"
        count = models.Proposal.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_user_cannot_create_proposal_past_phase(client, phase_factory, user):
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_post_phase(phase):
        response = client.get(url)
        assert response.status_code == 302
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_user_can_create_proposal_only_with_terms_agreement(
    client,
    phase_factory,
    user,
    category_factory,
    organisation_terms_of_use_factory,
    area_settings_factory,
):
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Proposal.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert_template_response(
            response, "a4_candy_budgeting/proposal_create_form.html"
        )
        assert response.status_code == 200
        proposal = {
            "name": "Proposal",
            "description": "description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
        }
        response = client.post(url, proposal)
        assert response.status_code == 200
        organisation_terms_of_use_factory(
            user=user,
            organisation=module.project.organisation,
            has_agreed=True,
        )
        response = client.post(url, proposal)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"
        count = models.Proposal.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_admin_can_create_proposal_past_phase(
    client, phase_factory, admin, category_factory, area_settings_factory
):
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_post_phase(phase):
        client.login(username=admin.email, password="password")
        response = client.get(url)
        assert_template_response(
            response, "a4_candy_budgeting/proposal_create_form.html"
        )
        assert response.status_code == 200
        proposal = {
            "name": "Proposal",
            "description": "description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, proposal)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"
        count = models.Proposal.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_user_can_create_proposal_with_creator_contact_fields(
    client, phase_factory, user, category_factory, area_settings_factory
):
    """Test that user can set creator email, phone, and consent when creating a proposal."""
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Proposal.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")

        proposal_data = {
            "name": "Proposal with contact info",
            "description": "description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
            "creator_email": "creator@example.com",
            "creator_phone": "+4915123456789",
            "creator_contact_consent": True,
        }
        response = client.post(url, proposal_data)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"

        count = models.Proposal.objects.all().count()
        assert count == 1

        proposal = models.Proposal.objects.first()
        assert proposal.creator_email == "creator@example.com"
        assert proposal.creator_phone == "+4915123456789"
        assert proposal.creator_contact_consent is True


@pytest.mark.django_db
def test_creator_contact_fields_not_saved_without_consent_on_proposal(
    client, phase_factory, user, category_factory, area_settings_factory
):
    """Test that email and phone are NOT saved when consent is not given."""
    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        proposal_data = {
            "name": "Proposal with contact info",
            "description": "description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
            "creator_email": "shouldnotsave@example.com",
            "creator_phone": "+4915123456789",
            "creator_contact_consent": False,
        }
        response = client.post(url, proposal_data)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"

        proposal = models.Proposal.objects.first()
        assert proposal.creator_email == ""
        assert proposal.creator_phone == ""
        assert proposal.creator_contact_consent is False


@pytest.mark.django_db
def test_guest_creator_email_not_prefilled_on_proposal_create_form(
    client, phase_factory, area_settings_factory
):
    from tests.helpers import GuestUserCreator

    phase = phase_factory(phase_content=phases.RequestPhase())
    module = phase.module
    project = module.project
    project.allow_guest_users = True
    project.save()
    area_settings_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    guest_user = GuestUserCreator().create_guest_user()
    with freeze_phase(phase):
        client.force_login(guest_user)
        response = client.get(url)
        assert_template_response(
            response, "a4_candy_budgeting/proposal_create_form.html"
        )
        form = response.context_data["form"]
        assert form.fields["creator_email"].initial in ("", None)

import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.ideas import models
from apps.ideas import phases


@pytest.mark.django_db
def test_create_view(
    client, phase_factory, idea_factory, user, category_factory, organisation
):
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={"organisation_slug": organisation.slug, "module_slug": module.slug},
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        response = client.get(url)
        assert_template_response(response, "a4_candy_ideas/idea_create_form.html")

        idea = {
            "name": "Idea",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, idea)
        assert redirect_target(response) == "idea-detail"


@pytest.mark.django_db
def test_anonymous_cannot_create_idea(client, phase_factory):
    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Idea.objects.all().count()
        assert count == 0
        response = client.get(url)
        assert response.status_code == 302
        assert redirect_target(response) == "account_login"


@pytest.mark.django_db
def test_user_can_create_idea_during_active_phase(
    client, phase_factory, user, category_factory
):
    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Idea.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert_template_response(response, "a4_candy_ideas/idea_create_form.html")
        assert response.status_code == 200
        idea = {
            "name": "Idea",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, idea)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"
        count = models.Idea.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_user_cannot_create_idea_in_wrong_phase(client, phase_factory, user):
    phase = phase_factory(phase_content=phases.RatingPhase())
    module = phase.module
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        response = client.get(url)
        assert response.status_code == 302
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_user_can_create_idea_only_with_terms_agreement(
    client, phase_factory, user, category_factory, organisation_terms_of_use_factory
):
    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Idea.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert_template_response(response, "a4_candy_ideas/idea_create_form.html")
        assert response.status_code == 200
        idea = {
            "name": "Idea",
            "description": "description",
            "category": category.pk,
        }
        response = client.post(url, idea)
        assert response.status_code == 200
        organisation_terms_of_use_factory(
            user=user,
            organisation=module.project.organisation,
            has_agreed=True,
        )
        response = client.post(url, idea)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"
        count = models.Idea.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_admin_can_create_idea_in_wrong_phase(
    client, phase_factory, category_factory, admin
):
    phase = phase_factory(phase_content=phases.RatingPhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=admin.email, password="password")
        response = client.get(url)
        assert_template_response(response, "a4_candy_ideas/idea_create_form.html")
        assert response.status_code == 200
        idea = {
            "name": "Idea",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, idea)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"
        count = models.Idea.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_user_can_create_idea_with_creator_contact_fields(
    client, phase_factory, user, category_factory
):
    """Test that user can set creator email, phone, and consent when creating an idea."""
    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Idea.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")

        idea_data = {
            "name": "Idea with contact info",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
            "creator_email": "creator@example.com",
            "creator_phone": "+4915123456789",
            "creator_contact_consent": True,
        }
        response = client.post(url, idea_data)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"

        count = models.Idea.objects.all().count()
        assert count == 1

        idea = models.Idea.objects.first()
        assert idea.creator_email == "creator@example.com"
        assert idea.creator_phone == "+4915123456789"
        assert idea.creator_contact_consent is True


@pytest.mark.django_db
def test_creator_contact_fields_not_saved_without_consent(
    client, phase_factory, user, category_factory
):
    """Test that creator email and phone are NOT saved when consent is not given.

    Business rule: If user does not check the consent checkbox, email and phone
    should be saved as empty strings regardless of what was submitted.
    """
    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        count = models.Idea.objects.all().count()
        assert count == 0
        client.login(username=user.email, password="password")

        idea_data = {
            "name": "Idea with contact info",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
            "creator_email": "shouldnotsave@example.com",
            "creator_phone": "+4915123456789",
            "creator_contact_consent": False,  # Consent NOT given
        }
        response = client.post(url, idea_data)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"

        count = models.Idea.objects.all().count()
        assert count == 1

        idea = models.Idea.objects.first()
        # Email and phone should be empty because consent was False
        assert idea.creator_email == "", "Email should be empty when consent is False"
        assert idea.creator_phone == "", "Phone should be empty when consent is False"
        assert idea.creator_contact_consent is False, "Consent should be saved as False"


@pytest.mark.django_db
def test_cannot_set_contact_fields_without_consent_on_create(
    client, phase_factory, user, category_factory
):
    """Test that email and phone cannot be saved without consent, even if provided."""
    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        idea_data = {
            "name": "Idea with contact info but no consent",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
            "creator_email": "wontsave@example.com",
            "creator_phone": "+9999999999",
            # creator_contact_consent omitted - defaults to False
        }
        response = client.post(url, idea_data)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"

        idea = models.Idea.objects.get(name="Idea with contact info but no consent")
        # Email and phone should be empty because consent defaults to False
        assert idea.creator_email == "", "Email should not be saved without consent"
        assert idea.creator_phone == "", "Phone should not be saved without consent"
        assert idea.creator_contact_consent is False


@pytest.mark.django_db
def test_guest_creator_email_not_prefilled_on_create_form(client, phase_factory):
    from tests.helpers import GuestUserCreator

    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    project = module.project
    project.allow_guest_users = True
    project.save()
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    guest_user = GuestUserCreator().create_guest_user()
    with freeze_phase(phase):
        client.force_login(guest_user)
        response = client.get(url)
        assert_template_response(response, "a4_candy_ideas/idea_create_form.html")
        form = response.context_data["form"]
        assert form.fields["creator_email"].initial in ("", None)

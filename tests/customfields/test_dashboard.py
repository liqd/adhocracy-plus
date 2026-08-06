import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import setup_phase
from apps.customfields.dashboard import CustomFieldComponent
from apps.customfields.models import CustomFieldSettings
from apps.ideas import phases


@pytest.mark.django_db
def test_component_effective_for_bs_blueprint(bs_module):
    assert CustomFieldComponent().is_effective(bs_module)


@pytest.mark.django_db
def test_component_not_effective_for_other_blueprints(phase_factory):
    phase, module, project, _ = setup_phase(phase_factory, None, phases.IssuePhase)
    module.blueprint_type = "IC"
    module.save()
    assert not CustomFieldComponent().is_effective(module)


@pytest.mark.django_db
def test_edit_view(client, bs_module):
    initiator = bs_module.project.organisation.initiators.first()
    url = CustomFieldComponent().get_base_url(bs_module)
    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert_template_response(
        response, "a4_candy_customfields/custom_field_settings.html"
    )


@pytest.mark.django_db
def test_edit_view_requires_initiator(client, bs_module, user):
    url = CustomFieldComponent().get_base_url(bs_module)
    client.login(username=user.email, password="password")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_settings_created_lazily(client, phase_factory):
    phase, module, project, _ = setup_phase(phase_factory, None, phases.IssuePhase)
    module.blueprint_type = "BS"
    module.save()
    assert not CustomFieldSettings.objects.filter(module=module).exists()

    initiator = project.organisation.initiators.first()
    url = CustomFieldComponent().get_base_url(module)
    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert response.status_code == 200
    assert CustomFieldSettings.objects.filter(module=module).exists()


@pytest.mark.django_db
def test_dashboard_menu_url_matches_component(client, bs_module):
    initiator = bs_module.project.organisation.initiators.first()
    url = CustomFieldComponent().get_base_url(bs_module)
    expected = reverse(
        "a4dashboard:custom-fields-dashboard",
        kwargs={
            "organisation_slug": bs_module.project.organisation.slug,
            "module_slug": bs_module.slug,
        },
    )
    assert url == expected
    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert response.status_code == 200

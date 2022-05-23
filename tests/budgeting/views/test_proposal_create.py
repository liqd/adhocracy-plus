import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import phases


@pytest.mark.django_db
def test_create_view(client, phase_factory, proposal_factory, user,
                     category_factory, area_settings_factory):
    phase, module, project, item = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase)
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse(
        'a4_candy_budgeting:proposal-create',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'module_slug': module.slug
        }
    )
    with freeze_phase(phase):
        client.login(username=user.email, password='password')

        response = client.get(url)
        assert_template_response(
            response,
            'a4_candy_budgeting/proposal_create_form.html')

        data = {
            'name': 'Idea',
            'description': 'description',
            'category': category.pk,
            'budget': 123,
            'point': (0, 0),
            'point_label': 'somewhere',
            'organisation_terms_of_use': True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == 'proposal-detail'

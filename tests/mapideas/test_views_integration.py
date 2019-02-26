import pytest
from django.core.urlresolvers import reverse

from adhocracy4.test.helpers import redirect_target
from liqd_product.apps.mapideas import phases
from tests.helpers import assert_template_response
from tests.helpers import freeze_phase
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_list_view(client, phase_factory, map_idea_factory, partner):
    phase, module, project, item = setup_phase(
        phase_factory, map_idea_factory, phases.FeedbackPhase)
    url = project.get_absolute_url()
    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(
            response, 'liqd_product_mapideas/mapidea_list.html')


@pytest.mark.django_db
def test_detail_view(client, phase_factory, map_idea_factory, partner):
    phase, module, project, item = setup_phase(
        phase_factory, map_idea_factory, phases.FeedbackPhase)
    url = item.get_absolute_url()
    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(
            response, 'liqd_product_mapideas/mapidea_detail.html')


@pytest.mark.django_db
def test_create_view(client, phase_factory, map_idea_factory, user,
                     category_factory, area_settings_factory, partner):
    phase, module, project, item = setup_phase(
        phase_factory, map_idea_factory, phases.CollectPhase)
    area_settings_factory(module=module)
    category = category_factory(module=module)
    url = reverse('liqd_product_mapideas:mapidea-create',
                  kwargs={'module_slug': module.slug})
    with freeze_phase(phase):
        client.login(username=user.email, password='password')

        response = client.get(url)
        assert_template_response(
            response, 'liqd_product_mapideas/mapidea_create_form.html')

        data = {
            'name': 'Idea',
            'description': 'description',
            'category': category.pk,
            'point': (0, 0),
            'point_label': 'somewhere'
        }
        response = client.post(url, data)
        assert redirect_target(response) == 'mapidea-detail'

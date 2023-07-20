from datetime import timedelta

import pytest
from dateutil.parser import parse
from django.urls import reverse

from adhocracy4.polls import phases
from adhocracy4.test.helpers import assert_template_response


@pytest.mark.django_db
def test_multi_module_timeline_initial_slide(
    client, project, module_factory, phase_factory, poll_factory
):
    modules = []
    for i in range(10):
        module = module_factory(project=project, weight=1)
        modules.append(module)
        poll_factory(module=module)
        phase_factory(
            module=module,
            phase_content=phases.VotingPhase(),
            start_date=parse("2013-01-01 17:00:00 UTC") + timedelta(hours=i),
            end_date=parse("2013-01-01 17:59:00 UTC") + timedelta(hours=i),
        )
    for index, module in enumerate(modules):
        url = reverse(
            "module-detail",
            kwargs={
                "organisation_slug": project.organisation.slug,
                "module_slug": module.slug,
            },
        )
        response = client.get(url)
        assert response.context_data["initial_slide"] == index
        assert_template_response(response, "a4polls/poll_detail.html")
        assert response.template_name[0] == "a4polls/poll_detail.html"

from pathlib import Path

import pytest
from django.urls import reverse

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import phases


@pytest.mark.django_db
def test_image_is_deleted_after_update(
    client,
    user,
    phase_factory,
    proposal_factory,
    category_factory,
    area_settings_factory,
    image_factory,
):
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)
    proposal.image = image_factory()
    proposal.save()

    image_path = Path(proposal.image.path)
    assert "ideas/images" in proposal.image.path

    with freeze_phase(phase):
        client.login(username=proposal.creator.email, password="password")
        # delete image
        url = reverse(
            "a4_candy_budgeting:proposal-delete",
            kwargs={
                "organisation_slug": proposal.project.organisation.slug,
                "pk": proposal.pk,
                "year": proposal.created.year,
            },
        )
        client.post(url, {}, format="json")

        assert not image_path.exists()

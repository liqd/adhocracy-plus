import pytest
from pytest_factoryboy import register

from adhocracy4.test.helpers import setup_phase
from apps.ideas import phases as idea_phases

from ..ideas import factories as ideas_factories
from ..mapideas import factories as mapideas_factories
from . import factories

register(factories.CustomFieldSettingsFactory)
register(factories.CustomFieldFactory)
register(factories.CustomFieldChoiceFactory)
register(ideas_factories.IdeaFactory)
register(mapideas_factories.MapIdeaFactory)


@pytest.fixture
def bs_module(phase_factory):
    """Module of the brainstorming blueprint with custom field settings."""
    phase, module, project, _ = setup_phase(phase_factory, None, idea_phases.IssuePhase)
    module.blueprint_type = "BS"
    module.save()
    factories.CustomFieldSettingsFactory(module=module)
    return module

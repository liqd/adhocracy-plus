import pytest

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import freeze_post_phase
from adhocracy4.test.helpers import setup_phase
from apps.interactiveevents import phases
from apps.interactiveevents import predicates
from apps.interactiveevents.models import LiveQuestion


@pytest.mark.django_db
def test_phase_allows_like_active(user, admin, phase_factory, live_question_factory):
    phase, _, _, livequestion = setup_phase(
        phase_factory, live_question_factory, phases.IssuePhase
    )

    with freeze_phase(phase):
        assert not predicates.phase_allows_like(user, False)
        assert predicates.phase_allows_like(user, livequestion)
        assert predicates.phase_allows_like(admin, livequestion)


@pytest.mark.django_db
def test_phase_allows_like_post(user, admin, phase_factory, live_question_factory):
    phase, _, _, livequestion = setup_phase(
        phase_factory, live_question_factory, phases.IssuePhase
    )

    with freeze_post_phase(phase):
        assert not predicates.phase_allows_like(user, False)
        assert not predicates.phase_allows_like(user, livequestion)
        assert not predicates.phase_allows_like(admin, livequestion)


@pytest.mark.django_db
def test_phase_allows_like_model_active(
    user, admin, phase_factory, live_question_factory
):
    phase, module, _, livequestion = setup_phase(
        phase_factory, live_question_factory, phases.IssuePhase
    )

    with freeze_phase(phase):
        assert not predicates.phase_allows_like_model(LiveQuestion)(user, False)
        assert predicates.phase_allows_like_model(LiveQuestion)(user, module)
        assert predicates.phase_allows_like_model(LiveQuestion)(admin, module)


@pytest.mark.django_db
def test_phase_allows_like_model_post(
    user, admin, phase_factory, live_question_factory
):
    phase, module, _, _ = setup_phase(
        phase_factory, live_question_factory, phases.IssuePhase
    )

    with freeze_post_phase(phase):
        assert not predicates.phase_allows_like_model(LiveQuestion)(user, False)
        assert not predicates.phase_allows_like_model(LiveQuestion)(user, module)
        assert not predicates.phase_allows_like_model(LiveQuestion)(admin, module)

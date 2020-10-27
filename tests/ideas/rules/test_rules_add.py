import pytest
import rules

from adhocracy4.projects.enums import Access
from apps.ideas import phases
from tests.helpers import freeze_phase
from tests.helpers import freeze_post_phase
from tests.helpers import freeze_pre_phase
from tests.helpers import setup_phase
from tests.helpers import setup_users

perm_name = 'a4_candy_ideas.add_idea'


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_pre_phase(phase_factory, user, member_factory):
    phase, module, project, _ = setup_phase(phase_factory, None,
                                            phases.CollectPhase)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_public
    with freeze_pre_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, module)
        assert not rules.has_perm(perm_name, user, module)
        assert not rules.has_perm(perm_name, member.member, module)
        assert rules.has_perm(perm_name, moderator, module)
        assert rules.has_perm(perm_name, initiator, module)


@pytest.mark.django_db
def test_phase_active(phase_factory, user, member_factory):
    phase, module, project, _ = setup_phase(phase_factory, None,
                                            phases.CollectPhase)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_public
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, module)
        assert rules.has_perm(perm_name, user, module)
        assert rules.has_perm(perm_name, member.member, module)
        assert rules.has_perm(perm_name, moderator, module)
        assert rules.has_perm(perm_name, initiator, module)


@pytest.mark.django_db
def test_phase_active_project_private(phase_factory, user, user2,
                                      member_factory):
    phase, module, project, _ = setup_phase(phase_factory, None,
                                            phases.CollectPhase,
                                            module__project__access=Access.
                                            PRIVATE)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    participant = user2
    project.participants.add(participant)

    assert not project.is_public
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, module)
        assert not rules.has_perm(perm_name, user, module)
        assert rules.has_perm(perm_name, participant, module)
        assert rules.has_perm(perm_name, member.member, module)
        assert rules.has_perm(perm_name, moderator, module)
        assert rules.has_perm(perm_name, initiator, module)


@pytest.mark.django_db
def test_phase_active_project_draft(phase_factory, user, member_factory):
    phase, module, project, _ = setup_phase(phase_factory, None,
                                            phases.CollectPhase,
                                            module__project__is_draft=True)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_draft
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, module)
        assert not rules.has_perm(perm_name, user, module)
        assert not rules.has_perm(perm_name, member.member, module)
        assert rules.has_perm(perm_name, moderator, module)
        assert rules.has_perm(perm_name, initiator, module)


@pytest.mark.django_db
def test_post_phase_project_archived(phase_factory, user, member_factory):
    phase, module, project, _ = setup_phase(phase_factory, None,
                                            phases.CollectPhase,
                                            module__project__is_archived=True)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_archived
    with freeze_post_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, module)
        assert not rules.has_perm(perm_name, user, module)
        assert not rules.has_perm(perm_name, member.member, module)
        assert rules.has_perm(perm_name, moderator, module)
        assert rules.has_perm(perm_name, initiator, module)

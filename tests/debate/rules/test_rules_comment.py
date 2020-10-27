import pytest
import rules

from adhocracy4.projects.enums import Access
from apps.debate import phases
from tests.helpers import freeze_phase
from tests.helpers import freeze_post_phase
from tests.helpers import freeze_pre_phase
from tests.helpers import setup_phase
from tests.helpers import setup_users

perm_name = 'a4_candy_debate.comment_subject'


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_pre_phase(phase_factory, subject_factory, user, member_factory):
    phase, _, project, item = setup_phase(phase_factory, subject_factory,
                                          phases.DebatePhase)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_public
    with freeze_pre_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, item)
        assert not rules.has_perm(perm_name, user, item)
        assert not rules.has_perm(perm_name, member.member, item)
        assert rules.has_perm(perm_name, moderator, item)
        assert rules.has_perm(perm_name, initiator, item)


@pytest.mark.django_db
def test_phase_active(phase_factory, subject_factory, user, member_factory):
    phase, _, project, item = setup_phase(phase_factory, subject_factory,
                                          phases.DebatePhase)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_public
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, item)
        assert rules.has_perm(perm_name, user, item)
        assert rules.has_perm(perm_name, member.member, item)
        assert rules.has_perm(perm_name, moderator, item)
        assert rules.has_perm(perm_name, initiator, item)


@pytest.mark.django_db
def test_phase_active_project_private(phase_factory, user, user2,
                                      member_factory, subject_factory):
    phase, _, project, item = setup_phase(phase_factory, subject_factory,
                                          phases.DebatePhase,
                                          module__project__access=Access.
                                          PRIVATE)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    participant = user2
    project.participants.add(participant)

    assert not project.is_public
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, item)
        assert not rules.has_perm(perm_name, user, item)
        assert rules.has_perm(perm_name, participant, item)
        assert rules.has_perm(perm_name, member.member, item)
        assert rules.has_perm(perm_name, moderator, item)
        assert rules.has_perm(perm_name, initiator, item)


@pytest.mark.django_db
def test_phase_active_project_draft(phase_factory, subject_factory, user,
                                    member_factory):
    phase, _, project, item = setup_phase(phase_factory, subject_factory,
                                          phases.DebatePhase,
                                          module__project__is_draft=True)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_draft
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, item)
        assert not rules.has_perm(perm_name, user, item)
        assert not rules.has_perm(perm_name, member.member, item)
        assert rules.has_perm(perm_name, moderator, item)
        assert rules.has_perm(perm_name, initiator, item)


@pytest.mark.django_db
def test_post_phase_project_archived(phase_factory, subject_factory, user,
                                     member_factory):
    phase, _, project, item = setup_phase(phase_factory, subject_factory,
                                          phases.DebatePhase,
                                          module__project__is_archived=True)
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert project.is_archived
    with freeze_post_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, item)
        assert not rules.has_perm(perm_name, user, item)
        assert not rules.has_perm(perm_name, member.member, item)
        assert rules.has_perm(perm_name, moderator, item)
        assert rules.has_perm(perm_name, initiator, item)

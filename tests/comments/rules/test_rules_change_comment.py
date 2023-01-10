import pytest
import rules

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import freeze_post_phase
from adhocracy4.test.helpers import freeze_pre_phase
from adhocracy4.test.helpers import setup_phase
from adhocracy4.test.helpers import setup_users
from apps.ideas import phases

perm_name = "a4comments.change_comment"


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_pre_phase(
    phase_factory, idea_factory, user, member_factory, admin, comment_factory
):
    phase, _, project, item = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    anonymous, moderator, initiator = setup_users(project)
    comment = comment_factory(content_object=item)
    creator = comment.creator
    member = member_factory(organisation=project.organisation)

    assert project.is_public
    with freeze_pre_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, comment)
        assert not rules.has_perm(perm_name, user, comment)
        assert not rules.has_perm(perm_name, member.member, comment)
        assert not rules.has_perm(perm_name, creator, comment)
        assert rules.has_perm(perm_name, admin, comment)
        assert not rules.has_perm(perm_name, moderator, comment)
        assert not rules.has_perm(perm_name, initiator, comment)


@pytest.mark.django_db
def test_phase_active(
    phase_factory, idea_factory, user, member_factory, admin, comment_factory
):
    phase, _, project, item = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    anonymous, moderator, initiator = setup_users(project)
    comment = comment_factory(content_object=item)
    creator = comment.creator
    member = member_factory(organisation=project.organisation)

    assert project.is_public
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, comment)
        assert not rules.has_perm(perm_name, user, comment)
        assert not rules.has_perm(perm_name, member.member, comment)
        assert rules.has_perm(perm_name, creator, comment)
        assert rules.has_perm(perm_name, admin, comment)
        assert not rules.has_perm(perm_name, moderator, comment)
        assert not rules.has_perm(perm_name, initiator, comment)


@pytest.mark.django_db
def test_phase_active_project_draft(
    phase_factory, idea_factory, user, member_factory, admin, comment_factory
):
    phase, _, project, item = setup_phase(
        phase_factory, idea_factory, phases.RatingPhase, module__project__is_draft=True
    )
    anonymous, moderator, initiator = setup_users(project)
    comment = comment_factory(content_object=item)
    creator = comment.creator
    member = member_factory(organisation=project.organisation)

    assert project.is_draft
    with freeze_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, comment)
        assert not rules.has_perm(perm_name, user, comment)
        assert not rules.has_perm(perm_name, member.member, comment)
        assert not rules.has_perm(perm_name, creator, comment)
        assert rules.has_perm(perm_name, admin, comment)
        assert not rules.has_perm(perm_name, moderator, comment)
        assert not rules.has_perm(perm_name, initiator, comment)


@pytest.mark.django_db
def test_post_phase_project_archived(
    phase_factory, idea_factory, user, member_factory, admin, comment_factory
):
    phase, _, project, item = setup_phase(
        phase_factory,
        idea_factory,
        phases.CollectPhase,
        module__project__is_archived=True,
    )
    anonymous, moderator, initiator = setup_users(project)
    comment = comment_factory(content_object=item)
    creator = comment.creator
    member = member_factory(organisation=project.organisation)

    assert project.is_archived
    with freeze_post_phase(phase):
        assert not rules.has_perm(perm_name, anonymous, comment)
        assert not rules.has_perm(perm_name, user, comment)
        assert not rules.has_perm(perm_name, member.member, comment)
        assert not rules.has_perm(perm_name, creator, comment)
        assert rules.has_perm(perm_name, admin, comment)
        assert not rules.has_perm(perm_name, moderator, comment)
        assert not rules.has_perm(perm_name, initiator, comment)

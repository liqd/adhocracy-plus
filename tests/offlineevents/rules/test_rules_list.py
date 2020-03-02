import pytest
import rules

from tests.helpers import setup_users

perm_name = 'a4_candy_offlineevents.list_offlineevent'


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_rule(offline_event, user, member_factory):
    project = offline_event.project
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=project.organisation)

    assert not rules.has_perm(perm_name, anonymous, project)
    assert not rules.has_perm(perm_name, user, project)
    assert not rules.has_perm(perm_name, member.member, project)
    assert rules.has_perm(perm_name, moderator, project)
    assert rules.has_perm(perm_name, initiator, project)

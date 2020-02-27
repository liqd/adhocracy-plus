import pytest
import rules

from tests.helpers import setup_users

perm_name = 'a4_candy_organisations.change_organisation'


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_rule(project, user, member_factory, admin):
    organisation = project.organisation
    anonymous, moderator, initiator = setup_users(project)
    member = member_factory(organisation=organisation)

    assert not rules.has_perm(perm_name, anonymous, organisation)
    assert not rules.has_perm(perm_name, user, organisation)
    assert not rules.has_perm(perm_name, moderator, organisation)
    assert not rules.has_perm(perm_name, member.member, organisation)
    assert rules.has_perm(perm_name, initiator, organisation)
    assert rules.has_perm(perm_name, admin, organisation)

import pytest
import rules

from adhocracy4.test.helpers import setup_users

perm_name = "a4_candy_userdashboard.view_moderation_dashboard"


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_rule(project, user, admin):
    anonymous, moderator, initiator = setup_users(project)

    assert not rules.has_perm(perm_name, anonymous)
    assert not rules.has_perm(perm_name, user)
    assert not rules.has_perm(perm_name, initiator)
    assert not rules.has_perm(perm_name, admin)
    assert rules.has_perm(perm_name, moderator)

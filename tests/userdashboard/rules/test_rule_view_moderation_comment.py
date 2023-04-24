import pytest
import rules

from adhocracy4.test.helpers import setup_users

perm_name = "a4_candy_userdashboard.view_moderation_comment"


def test_perm_exists():
    assert rules.perm_exists(perm_name)


@pytest.mark.django_db
def test_rule(group_factory, project_factory, user_factory, admin):
    user = user_factory()
    group_member = user_factory()
    group = group_factory()
    group.user_set.add(group_member)
    project1 = project_factory(group=group)
    project2 = project_factory()
    anonymous1, moderator1, initiator1 = setup_users(project1)
    anonymous2, moderator2, initiator2 = setup_users(project2)

    assert admin.has_perm(perm_name, project1)
    assert not user.has_perm(perm_name, project1)
    assert group_member.has_perm(perm_name, project1)
    assert not anonymous1.has_perm(perm_name, project1)
    assert moderator1.has_perm(perm_name, project1)
    assert initiator1.has_perm(perm_name, project1)
    assert not moderator2.has_perm(perm_name, project1)
    assert not initiator2.has_perm(perm_name, project1)

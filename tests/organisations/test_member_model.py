import pytest


@pytest.mark.django_db
def test_string_representation(member):
    string_repr = '{}_{}'.format(member.organisation, member.member)
    assert str(member) == string_repr

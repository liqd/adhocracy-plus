import pytest


@pytest.mark.django_db
def test_string_representation(organisation_terms_of_use):
    string_repr = "{}_{}".format(
        organisation_terms_of_use.organisation, organisation_terms_of_use.user
    )
    assert str(organisation_terms_of_use) == string_repr

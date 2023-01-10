import pytest
from django import forms

from apps.debate.models import Subject
from apps.organisations.mixins import OrganisationTermsOfUseMixin


class SubjectForm(OrganisationTermsOfUseMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop("module")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ["name", "creator", "module"]


@pytest.mark.django_db
def test_del_field(user, organisation, module, organisation_terms_of_use_factory):
    form = SubjectForm(user=user, module=module)
    assert "organisation_terms_of_use" in form.fields
    organisation_terms_of_use_factory(
        user=user, organisation=module.project.organisation, has_agreed=True
    )
    form = SubjectForm(user=user, module=module)
    assert "organisation_terms_of_use" not in form.fields


@pytest.mark.django_db
def test_clean(user, organisation, module):
    data = {
        "name": "Subject name",
        "organisation_terms_of_use": False,
    }
    form = SubjectForm(user=user, module=module, data=data)
    assert not form.is_valid()
    assert form["organisation_terms_of_use"].errors[0].startswith("Please agree on")


@pytest.mark.django_db
def test_save(user, organisation, module, organisation_terms_of_use_factory):
    agreed = organisation_terms_of_use_factory(
        user=user, organisation=module.project.organisation, has_agreed=False
    )
    assert not agreed.has_agreed
    data = {
        "name": "Subject name",
        "creator": user,
        "module": module,
        "organisation_terms_of_use": True,
    }
    form = SubjectForm(user=user, module=module, data=data)
    form.save()
    agreed.refresh_from_db()
    assert agreed.has_agreed

from django import forms
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from apps.organisations.models import OrganisationTermsOfUse


class OrganisationTermsOfUseMixin(forms.ModelForm):
    """
    Add org terms checkbox to form when user has not yet agreed.

    Make sure, that the user is added to the form_kwargs in the
    respective view. You can use the UserFormViewMixin to do that.
    """

    organisation_terms_of_use = forms.BooleanField(
        required=False,
        help_text=_("You can still manage all your preferences on User Agreements."),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["organisation_terms_of_use"].label = self._get_terms_of_use_label

        if self.user.has_agreed_on_org_terms(self.module.project.organisation):
            del self.fields["organisation_terms_of_use"]

    def clean(self):
        cleaned_data = super().clean()
        if "organisation_terms_of_use" in cleaned_data:
            organisation_terms_of_use = cleaned_data.get("organisation_terms_of_use")
            if not organisation_terms_of_use:
                self.add_error(
                    "organisation_terms_of_use",
                    _(
                        "Please agree on the organisation's terms "
                        "of use to be allowed to create content."
                    ),
                )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit and "organisation_terms_of_use" in self.cleaned_data:
            OrganisationTermsOfUse.objects.update_or_create(
                user=self.user,
                organisation=self.module.project.organisation,
                defaults={"has_agreed": self.cleaned_data["organisation_terms_of_use"]},
            )
        return instance

    def _get_terms_of_use_label(self):
        label_text = _(
            "Yes, I have read and agree to this organisation's " "{}terms of use{}."
        )
        url = reverse(
            "organisation-terms-of-use",
            kwargs={"organisation_slug": self.module.project.organisation.slug},
        )
        label = label_text.format('<a href="' + url + '" target="_blank">', "</a>")
        return mark_safe(label)


class UserFormViewMixin(FormView):
    """Adds the user from the request to the form_kwargs."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

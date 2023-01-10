from django import forms
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.organisations.models import OrganisationTermsOfUse
from apps.users.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "_avatar",
            "bio",
            "homepage",
            "facebook_handle",
            "twitter_handle",
            "get_notifications",
            "get_newsletters",
            "language",
        ]

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.get(username__iexact=username)
            if user != self.instance:
                raise forms.ValidationError(
                    User._meta.get_field("username").error_messages["unique"]
                )
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(email__iexact=username)
            if user != self.instance:
                raise forms.ValidationError(
                    User._meta.get_field("username").error_messages["used_as_email"]
                )
        except User.DoesNotExist:
            pass

        return username


class OrganisationTermsOfUseForm(forms.ModelForm):
    class Meta:
        model = OrganisationTermsOfUse
        exclude = ()


class OrganisationsTermsOfUseInlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            organisation = form.instance.organisation
            form.fields["has_agreed"].label = self._get_terms_of_use_label(organisation)

    def _get_terms_of_use_label(self, organisation):
        label_text = _(
            "Yes, I have read and agree to this organisation's " "{}terms of use{}."
        )
        url = reverse(
            "organisation-terms-of-use", kwargs={"organisation_slug": organisation.slug}
        )
        label = label_text.format('<a href="' + url + '" target="_blank">', "</a>")
        return mark_safe(label)


OrganisationTermsOfUseFormSet = forms.inlineformset_factory(
    User,
    OrganisationTermsOfUse,
    form=OrganisationTermsOfUseForm,
    formset=OrganisationsTermsOfUseInlineFormSet,
    fields=["has_agreed"],
    can_delete=False,
    extra=0,
)

from django import forms
from django.utils.translation import ugettext_lazy as _

from liqd_product.apps.organisations.models import Organisation


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['name', 'logo']
        labels = {
            'name': _('Organisation name')
        }

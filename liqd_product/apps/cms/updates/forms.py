from django import forms

from .models import KeepMeUpdatedEmail


class KeepMeUpdatedEmailForm(forms.ModelForm):

    class Meta:
        model = KeepMeUpdatedEmail
        fields = '__all__'

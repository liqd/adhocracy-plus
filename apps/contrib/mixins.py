from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import generic

RIGHT_OF_USE_LABEL = _('I hereby confirm that the copyrights for this '
                       'photo are with me or that I have received '
                       'rights of use from the author. I also confirm '
                       'that the privacy rights of depicted third persons '
                       'are not violated. ')


class DynamicChoicesMixin(object):
    """Dynamic choices mixin.

    Add callable functionality to filters that support the ``choices``
    argument. If the ``choices`` is callable, then it **must** accept the
    ``view`` object as a single argument.
    The ``view`` object may be None if the parent FilterSet is not class based.

    This is useful for dymanic ``choices`` determined properties on the
    ``view`` object.
    """

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        super().__init__(*args, **kwargs)

    def get_choices(self, view):
        choices = self.choices

        if callable(choices):
            return choices(view)
        return choices

    @property
    def field(self):
        choices = self.get_choices(getattr(self, 'view', None))

        if choices is not None:
            self.extra['choices'] = choices

        return super(DynamicChoicesMixin, self).field


class ImageRightOfUseMixin(forms.ModelForm):
    right_of_use = forms.BooleanField(required=False, label=RIGHT_OF_USE_LABEL)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.image:
            self.initial['right_of_use'] = True

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        right_of_use = cleaned_data.get('right_of_use')
        if image and not right_of_use:
            self.add_error('right_of_use',
                           _("You want to upload an image. "
                             "Please check that you have the "
                             "right of use for the image."))


class ProjectModuleDispatchMixin(generic.DetailView):

    @cached_property
    def project(self):
        return self.get_object()

    @cached_property
    def module(self):
        if self.modules.count() == 1 and not self.events:
            return self.modules.first()
        elif len(self.get_current_modules()) == 1:
            return self.get_current_modules()[0]

    def dispatch(self, request, *args, **kwargs):
        kwargs['project'] = self.project
        kwargs['module'] = self.module

        if self.modules.count() == 1 and not self.events:
            return self._view_by_phase()(request, *args, **kwargs)
        elif len(self.get_current_modules()) == 1:
            return self._view_by_phase()(request, *args, **kwargs)
        else:
            return super().dispatch(request)

    def _view_by_phase(self):
        if self.module.last_active_phase:
            return self.module.last_active_phase.view.as_view()
        elif self.module.future_phases:
            return self.module.future_phases.first().view.as_view()
        else:
            return super().dispatch

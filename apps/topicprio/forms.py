from ckeditor_uploader import fields
from django.utils.translation import gettext_lazy as _

from adhocracy4.categories.forms import CategorizableFieldMixin
from adhocracy4.labels.mixins import LabelsAddableFieldMixin
from apps.organisations.mixins import OrganisationTermsOfUseMixin

from . import models


class TopicForm(CategorizableFieldMixin,
                LabelsAddableFieldMixin,
                OrganisationTermsOfUseMixin):

    description = fields.RichTextUploadingFormField(
        config_name='image-editor',
        required=True,
        label=_('Description'))

    class Meta:
        model = models.Topic
        fields = ['name', 'description', 'category', 'labels']

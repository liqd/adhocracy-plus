from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.categories import models as category_models
from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import ModuleFormSetComponent
from adhocracy4.dashboard import components

from . import forms
from . import views

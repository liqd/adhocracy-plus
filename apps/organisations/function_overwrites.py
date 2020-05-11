from django.urls import reverse

from adhocracy4.dashboard.components.forms import ModuleFormComponent
from adhocracy4.dashboard.components.forms import ProjectFormComponent
from adhocracy4.modules.models import Module
from adhocracy4.projects.models import Project


def module_get_absolute_url(self):
    return reverse('module-detail', kwargs={
        'organisation_slug': self.project.organisation.slug,
        'module_slug': self.slug
    })


def project_get_absolute_url(self):
    return reverse('project-detail', kwargs={
        'organisation_slug': self.organisation.slug,
        'slug': self.slug
    })


def project_get_base_url(self, project):
    name = 'a4dashboard:dashboard-{identifier}-edit'.format(
        identifier=self.identifier)
    return reverse(name, kwargs={
        'organisation_slug': project.organisation.slug,
        'project_slug': project.slug
    })


def module_get_base_url(self, module):
    name = 'a4dashboard:dashboard-{identifier}-edit'.format(
        identifier=self.identifier)
    return reverse(name, kwargs={
        'organisation_slug': module.project.organisation.slug,
        'module_slug': module.slug
    })


Module.add_to_class("get_absolute_url", module_get_absolute_url)
Project.add_to_class("get_absolute_url", project_get_absolute_url)
ProjectFormComponent.get_base_url = project_get_base_url
ModuleFormComponent.get_base_url = module_get_base_url

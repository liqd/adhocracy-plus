from django import template

register = template.Library()


@register.filter
def project_url(project):
    return project.get_absolute_url()


@register.assignment_tag
def to_class_name(value):
    return value.__class__.__name__

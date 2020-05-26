from django import template

register = template.Library()


@register.filter
def is_publishable(project, project_progress):
    """Check if project can be published.

    Required project details need to be filled in and at least one module
    has to be published (added to the project).
    """
    return (project_progress['project_is_complete']
            and project.published_modules.count() >= 1)

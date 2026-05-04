from django import template
from django.urls import reverse

register = template.Library()

_CURRENT_ORGANISATION = "organisation"
_CURRENT_PROJECT = "project"
_CURRENT_MODULE = "module"
_CURRENT_ITEM = "item"


@register.inclusion_tag("includes/platform_breadcrumbs.html")
def platform_breadcrumbs(
    organisation=None,
    project=None,
    module=None,
    item_name=None,
    item_kind_label=None,
    current=_CURRENT_ORGANISATION,
):
    """
    Build hierarchy breadcrumbs: organisation name → project → module → (optional item).

    Only display names (truncated in the template). ``item_kind_label`` is kept
    for backwards compatibility with callers but is not shown.

    Resolve organisation/project from module when omitted.
    """
    if module is not None and project is None:
        project = module.project
    if project is not None and organisation is None:
        organisation = project.organisation

    if organisation is None:
        return {"crumbs": [], "show_trailing_separator": False}

    crumbs = []
    org_url = reverse("organisation", kwargs={"organisation_slug": organisation.slug})

    crumbs.append(
        {
            "name": organisation.name,
            "url": None if current == _CURRENT_ORGANISATION else org_url,
            "full_name": str(organisation.name),
        }
    )

    if current == _CURRENT_ORGANISATION:
        return {"crumbs": crumbs, "show_trailing_separator": True}

    if project is not None:
        crumbs.append(
            {
                "name": project.name,
                "url": (
                    None if current == _CURRENT_PROJECT else project.get_absolute_url()
                ),
                "full_name": str(project.name),
            }
        )

    if current == _CURRENT_PROJECT:
        return {"crumbs": crumbs, "show_trailing_separator": False}

    if module is not None:
        crumbs.append(
            {
                "name": module.name,
                "url": None if current == _CURRENT_MODULE else module.get_detail_url(),
                "full_name": str(module.name),
            }
        )

    if current == _CURRENT_MODULE:
        return {"crumbs": crumbs, "show_trailing_separator": False}

    if current == _CURRENT_ITEM and item_name:
        crumbs.append(
            {
                "name": item_name,
                "url": None,
                "full_name": str(item_name),
            }
        )

    return {"crumbs": crumbs, "show_trailing_separator": False}

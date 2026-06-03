from django import template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

register = template.Library()

_CURRENT_ORGANISATION = "organisation"
_CURRENT_PROJECT = "project"
_CURRENT_INFORMATION = "information"
_CURRENT_RESULTS = "results"
_CURRENT_MODULE = "module"
_CURRENT_ITEM = "item"

_PROJECT_SUBPAGE_LABELS = {
    _CURRENT_INFORMATION: _("Information"),
    _CURRENT_RESULTS: _("Statistics & Results"),
}


def _resolve_entities(organisation, project, module):
    if module is not None and project is None:
        project = module.project
    if project is not None and organisation is None:
        organisation = project.organisation
    return organisation, project, module


def _crumb(name, url=None):
    return {
        "name": name,
        "url": url,
        "full_name": str(name),
    }


def _breadcrumb_context(crumbs, show_trailing_separator=False):
    return {"crumbs": crumbs, "show_trailing_separator": show_trailing_separator}


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
    organisation, project, module = _resolve_entities(organisation, project, module)

    if organisation is None:
        return _breadcrumb_context([])

    org_url = reverse("organisation", kwargs={"organisation_slug": organisation.slug})
    crumbs = [
        _crumb(
            organisation.name,
            url=None if current == _CURRENT_ORGANISATION else org_url,
        )
    ]

    if current == _CURRENT_ORGANISATION:
        return _breadcrumb_context(crumbs, show_trailing_separator=True)

    if project is not None:
        crumbs.append(
            _crumb(
                project.name,
                url=None if current == _CURRENT_PROJECT else project.get_absolute_url(),
            )
        )

    if current == _CURRENT_PROJECT:
        return _breadcrumb_context(crumbs)

    subpage_label = _PROJECT_SUBPAGE_LABELS.get(current)
    if subpage_label is not None:
        crumbs.append(_crumb(subpage_label))
        return _breadcrumb_context(crumbs)

    if module is not None:
        crumbs.append(
            _crumb(
                module.name,
                url=None if current == _CURRENT_MODULE else module.get_detail_url(),
            )
        )

    if current == _CURRENT_MODULE:
        return _breadcrumb_context(crumbs)

    if current == _CURRENT_ITEM and item_name:
        crumbs.append(_crumb(item_name))

    return _breadcrumb_context(crumbs)

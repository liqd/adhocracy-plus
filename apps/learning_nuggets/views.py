import re
from html import unescape

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext
from django.utils.translation import ngettext
from django.views.generic import DetailView
from django.views.generic import ListView

from .models import LearningCategory
from .models import LearningCenterPage
from .models import LearningNuggetPage


def live_public_nuggets():
    """Only live pages that are not inside a private section.

    The custom Learning Center views bypass ``wagtail.urls``, so the standard
    live / privacy filtering has to be applied explicitly.
    """
    return (
        LearningNuggetPage.objects.live()
        .public()
        .select_related("category")
        .order_by("order")
    )


def _block_matches(block, query):
    """Return whether a single StreamField block matches ``query``.

    The acceptance criteria define three searchable fields: the page title
    (handled by the caller), the nugget title and the nugget description.
    """
    if block.block_type != "learning_nugget":
        return False

    value = block.value
    title = value.get("title") or ""
    if query in title.casefold():
        return True

    description = value.get("description")
    if description:
        # RichText exposes the raw HTML in ``source``. Replace tags with a
        # space (so words from adjacent blocks do not get glued together) and
        # decode entities before matching the visible text.
        text = getattr(description, "source", None) or str(description)
        text = unescape(re.sub(r"<[^>]+>", " ", text)).replace("\xa0", " ")
        if query in text.casefold():
            return True
    return False


def search_nuggets(query):
    """Return live, public nuggets matching ``query``.

    Matching is case-insensitive and finds partial words. The curated help
    content is filtered in Python because a database ``icontains`` lookup on
    the StreamField would also match media/document metadata instead of only
    the nugget title and description.
    """
    normalised = query.casefold()
    if not normalised:
        return []

    return [
        nugget
        for nugget in live_public_nuggets().filter(category__isnull=False)
        if normalised in nugget.title.casefold()
        or any(_block_matches(block, normalised) for block in nugget.content)
    ]


def build_search_summary(query, result_count):
    """Human readable (and translatable) summary of a sidebar search."""
    if not result_count:
        return gettext("No results for “%(query)s”.") % {"query": query}
    return ngettext(
        "%(count)s result for “%(query)s”",
        "%(count)s results for “%(query)s”",
        result_count,
    ) % {"count": result_count, "query": query}


class HtmxTemplateMixin:
    """Mixin to serve the partial template for htmx requests.

    Non-htmx requests fall back to the full page so the sidebar also works
    without JavaScript (progressive enhancement).
    """

    htmx_template_name = None

    @property
    def is_htmx(self):
        return self.request.htmx

    def get_template_names(self):
        if self.is_htmx and self.htmx_template_name:
            return [self.htmx_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_htmx"] = self.is_htmx
        return context


class LearningCenterView(HtmxTemplateMixin, ListView):
    template_name = "a4_candy_learning_nuggets/learning_center.html"
    htmx_template_name = "a4_candy_learning_nuggets/includes/nuggets_index.html"
    context_object_name = "grouped_categories"
    model = LearningCategory

    PERMISSION_ORDER = ["teilnehmer:in", "initiator:in", "moderator:in"]

    def get_queryset(self):
        return super().get_queryset().order_by("order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # The custom view does not go through Wagtail's page serving, so the
        # page (used for the heading) is looked up once here for both the full
        # page and the htmx partial.
        context["page"] = LearningCenterPage.objects.live().public().first()

        # Live sidebar search. The query is capped to keep pathological input
        # from being echoed back (and matched) in full.
        query = self.request.GET.get("q", "").strip()[:100]
        context["query"] = query
        context["nuggets"] = search_nuggets(query) if query else []
        context["search_summary"] = (
            build_search_summary(query, len(context["nuggets"])) if query else ""
        )

        if query:
            # Search results replace the category index in the partial.
            return context

        categories = list(context.get("grouped_categories", []))

        grouped = {}
        for category in categories:
            grouped.setdefault(category.permission_level, []).append(category)

        # Show the known permission levels first, but never drop categories that
        # store an unexpected level (e.g. legacy values that were never migrated).
        ordered_levels = [level for level in self.PERMISSION_ORDER if level in grouped]
        ordered_levels += [
            level for level in grouped if level not in self.PERMISSION_ORDER
        ]

        context["grouped_categories"] = [
            {"permission_level": level, "categories": grouped[level]}
            for level in ordered_levels
        ]

        return context


class LearningCategoryView(HtmxTemplateMixin, DetailView):
    """View for a specific category, showing all nuggets in that category"""

    template_name = "a4_candy_learning_nuggets/learning_category.html"
    htmx_template_name = "a4_candy_learning_nuggets/includes/nuggets_list.html"
    context_object_name = "category"

    def get_object(self):
        return get_object_or_404(LearningCategory, slug=self.kwargs["category_slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Evaluate the (live, public, ordered) nuggets once and reuse the list.
        context["nuggets"] = list(self.object.ordered_nuggets())
        return context


class LearningNuggetView(HtmxTemplateMixin, DetailView):
    """View for a specific learning nugget"""

    template_name = "a4_candy_learning_nuggets/learning_nugget_page.html"
    htmx_template_name = "a4_candy_learning_nuggets/includes/nugget_detail.html"
    context_object_name = "nugget"

    def get_object(self):
        # Get the nugget based on the slug, ensuring it belongs to the correct
        # category and is live / not private.
        category = get_object_or_404(
            LearningCategory, slug=self.kwargs["category_slug"]
        )
        return get_object_or_404(
            live_public_nuggets(),
            slug=self.kwargs["nugget_slug"],
            category=category,
        )

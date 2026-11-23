import difflib
import re
from html import unescape

from django.http import Http404
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
        .select_related("category", "icon")
        .order_by("order")
    )


def live_public_center():
    """Return the live Learning Center page if it is publicly viewable.

    The custom views bypass ``wagtail.urls``, so the page's own view
    restrictions are not enforced by Wagtail. If a center exists but is
    private, the whole Learning Center is hidden (mirroring the ``.public()``
    filtering used for nuggets).
    """
    page = LearningCenterPage.objects.live().public().first()
    if page is None and LearningCenterPage.objects.live().exists():
        raise Http404
    return page


WORD_RE = re.compile(r"\w+")
UMLAUT_TRANSLATION = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss"})

# German plural endings, longest first. The second value is the number of
# characters that must remain so short singulars (e.g. "Kurs") are not mangled.
PLURAL_ENDINGS = (
    ("innen", 3),
    ("ern", 4),
    ("en", 3),
    ("er", 4),
    ("e", 3),
    ("n", 4),
    ("s", 4),
)


def _stem(word):
    """Reduce a German word to a rough stem so singular and plural match."""
    word = word.casefold().translate(UMLAUT_TRANSLATION)
    for ending, min_remaining in PLURAL_ENDINGS:
        if word.endswith(ending) and len(word) - len(ending) >= min_remaining:
            return word[: -len(ending)]
    return word


def _words_match(query_word, text_word):
    """Match two stems, allowing a prefix relation for partial words."""
    if query_word == text_word:
        return True

    shorter, longer = sorted((query_word, text_word), key=len)
    return len(shorter) >= 4 and longer.startswith(shorter)


def matches_text(text, query):
    """Case-insensitive match with basic German singular/plural support.

    The plain substring check keeps prefix searches such as "regist" ->
    "Registration" working. The token/stem comparison additionally makes
    "Profile" match "Profil" without introducing a search backend.
    """
    normalised_query = query.casefold()
    if normalised_query in text.casefold():
        return True

    query_words = [_stem(word) for word in WORD_RE.findall(normalised_query)]
    if not query_words:
        return False

    text_words = {_stem(word) for word in WORD_RE.findall(text)}
    return all(
        any(_words_match(query_word, text_word) for text_word in text_words)
        for query_word in query_words
    )


def _description_text(description):
    """Return the visible text of a rich text description."""
    text = getattr(description, "source", None) or str(description)
    return unescape(re.sub(r"<[^>]+>", " ", text)).replace("\xa0", " ")


def _block_matches(block, query):
    """Return whether a single StreamField block matches ``query``.

    The acceptance criteria define three searchable fields: the page title
    (handled by the caller), the nugget title and the nugget description.
    """
    if block.block_type != "learning_nugget":
        return False

    value = block.value
    if matches_text(value.get("title") or "", query):
        return True

    description = value.get("description")
    if description:
        # RichText exposes the raw HTML in ``source``. Replace tags with a
        # space (so words from adjacent blocks do not get glued together) and
        # decode entities before matching the visible text.
        if matches_text(_description_text(description), query):
            return True
    return False


def search_nuggets(query):
    """Return live, public nuggets matching ``query``.

    Matching is case-insensitive, finds partial words and understands common
    German singular/plural pairs. The curated help content is filtered in
    Python because a database ``icontains`` lookup on the StreamField would
    also match media/document metadata instead of only the nugget title and
    description.
    """
    if not query:
        return []

    return [
        nugget
        for nugget in live_public_nuggets().filter(category__isnull=False)
        if matches_text(nugget.title, query)
        or any(_block_matches(block, query) for block in nugget.content)
    ]


FUZZY_CUTOFF = 0.75
FUZZY_MIN_WORD_LENGTH = 4


def _nugget_search_tokens(nugget):
    """Collect the searchable tokens of a single nugget."""
    tokens = set(WORD_RE.findall(nugget.title.casefold()))
    for block in nugget.content:
        if block.block_type != "learning_nugget":
            continue
        value = block.value
        tokens.update(WORD_RE.findall((value.get("title") or "").casefold()))
        description = value.get("description")
        if description:
            tokens.update(WORD_RE.findall(_description_text(description).casefold()))
    return tokens


def correct_search_query(query):
    """Return a typo-corrected query, or ``None`` if nothing was corrected.

    Only words of a useful length are compared. This is deliberately a plain
    string-similarity correction, not a semantic search.
    """
    query_words = WORD_RE.findall(query)
    if not query_words:
        return None

    vocabulary = set()
    for nugget in live_public_nuggets().filter(category__isnull=False):
        vocabulary.update(_nugget_search_tokens(nugget))
    vocabulary = sorted(
        word for word in vocabulary if len(word) >= FUZZY_MIN_WORD_LENGTH
    )
    if not vocabulary:
        return None

    corrected_words = []
    changed = False
    for word in query_words:
        normalised = word.casefold()
        if len(normalised) < FUZZY_MIN_WORD_LENGTH:
            corrected_words.append(word)
            continue

        matches = difflib.get_close_matches(
            normalised, vocabulary, n=1, cutoff=FUZZY_CUTOFF
        )
        if matches:
            replacement = matches[0]
            if word[:1].isupper():
                replacement = replacement[:1].upper() + replacement[1:]
            corrected_words.append(replacement)
            changed = changed or replacement.casefold() != normalised
        else:
            corrected_words.append(word)

    if not changed:
        return None
    return " ".join(corrected_words)


def search_nuggets_with_correction(query):
    """Search normally and only retry with a typo correction on no results."""
    results = search_nuggets(query)
    if results:
        return results, None

    corrected_query = correct_search_query(query)
    if corrected_query:
        results = search_nuggets(corrected_query)
        if results:
            return results, corrected_query

    return [], None


def build_search_summary(query, result_count, corrected_query=None):
    """Human readable (and translatable) summary of a sidebar search."""
    result_query = corrected_query or query
    if not result_count:
        return gettext("No results for “%(query)s”.") % {"query": query}

    result_summary = ngettext(
        "%(count)s result for “%(query)s”",
        "%(count)s results for “%(query)s”",
        result_count,
    ) % {"count": result_count, "query": result_query}

    if corrected_query:
        return gettext("No exact results for “%(query)s”. %(results)s") % {
            "query": query,
            "results": result_summary,
        }
    return result_summary


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

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("permission_level")
            .order_by("order", "name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # The custom view does not go through Wagtail's page serving, so the
        # page (used for the heading) is looked up once here for both the full
        # page and the htmx partial. This also enforces its view restrictions.
        context["page"] = live_public_center()

        # Live sidebar search. The query is capped to keep pathological input
        # from being echoed back (and matched) in full.
        query = self.request.GET.get("q", "").strip()[:100]
        context["query"] = query
        if query:
            context["nuggets"], context["search_correction"] = (
                search_nuggets_with_correction(query)
            )
            context["search_summary"] = build_search_summary(
                query,
                len(context["nuggets"]),
                context["search_correction"],
            )
        else:
            context["nuggets"] = []
            context["search_correction"] = None
            context["search_summary"] = ""

        if query:
            # Search results replace the category index in the partial.
            return context

        categories = list(context.get("grouped_categories", []))

        # One query for all visible nuggets keeps the per-category lists free
        # of N+1 queries.
        nuggets_by_category = {}
        for nugget in live_public_nuggets().filter(category__isnull=False):
            nuggets_by_category.setdefault(nugget.category_id, []).append(nugget)

        grouped = {}
        for category in categories:
            level = category.permission_level
            key = level.pk if level else None
            group = grouped.setdefault(
                key, {"permission_level": level, "categories": []}
            )
            group["categories"].append(
                {
                    "category": category,
                    "nuggets": nuggets_by_category.get(category.pk, []),
                }
            )

        # Order by the editable permission level order; categories without a
        # permission level are always shown last so they are never dropped.
        context["grouped_categories"] = sorted(
            grouped.values(),
            key=lambda group: (
                group["permission_level"] is None,
                group["permission_level"].order if group["permission_level"] else 0,
                group["permission_level"].name if group["permission_level"] else "",
            ),
        )

        return context


class LearningCategoryView(HtmxTemplateMixin, DetailView):
    """View for a specific category, showing all nuggets in that category"""

    template_name = "a4_candy_learning_nuggets/learning_category.html"
    htmx_template_name = "a4_candy_learning_nuggets/includes/nuggets_list.html"
    context_object_name = "category"

    def get_object(self):
        # A restricted Learning Center also hides its category listings.
        live_public_center()
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

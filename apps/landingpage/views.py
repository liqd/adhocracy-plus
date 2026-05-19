import random

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.cms.contacts.models import FormPage
from apps.cms.news.models import NewsIndexPage
from apps.cms.pages.models import SimplePage

from .models import StatisticsItem


def landing_view(request):
    # Get statistics
    items = list(StatisticsItem.objects.all().order_by("order"))
    random.shuffle(items)

    contact_form_page = None
    contact_form = None
    form_page = FormPage.objects.live().filter(slug="contact").first()
    if form_page:
        contact_form_page = form_page.specific
        contact_form = contact_form_page.get_form()

    news_block = None
    news_index = NewsIndexPage.objects.live().first()
    if news_index:
        latest_news = list(news_index.news[:3])
        news_block = {"news_page": news_index, "latest_news": latest_news}

    faq_page = SimplePage.objects.live().filter(slug="lpfaq").first()

    # Split statistics
    columns = [items[i::4] for i in range(4)]
    directions = ["down", "up", "down", "up"]

    mobile_rows = [columns[0] + columns[1], columns[2] + columns[3]]

    # Module data
    modules = [
        {
            "id": "poll",
            "name": _("Poll"),
            "icon": "images/poll-transparent.svg",
            "video_path": "images/poll_",
            "description": _(
                "Participants can answer open and multiple choice questions and comment on the poll."
            ),
            "features": [
                _("Gathering opinions and gauging public sentiment"),
                _("Prioritising topics or measures"),
                _("Evaluating concepts or planning proposals"),
                _("Capturing needs and requirements"),
            ],
        },
        {
            "id": "brainstorming",
            "name": _("Brainstorming"),
            "icon": "images/brainstorming-transparent.svg",
            "video_path": "images/brainstorming_",
            "description": _(
                "Participants can submit their own ideas and discuss the ideas of others."
            ),
            "features": [
                _("Open idea generation and creative participation"),
                _("Developing solutions to specific challenges"),
                _("Collecting project ideas or programme proposals"),
                _("Citizen engagement without a spatial reference"),
            ],
        },
        {
            "id": "spatial",
            "name": _("Spatial Brainstorming"),
            "icon": "images/spatial-brainstorming-transparent.svg",
            "video_path": "images/spatial_",
            "description": _(
                "Participants can submit their own ideas and locate them on a map. They can also discuss the ideas of others."
            ),
            "features": [
                _("Spatial planning and urban development"),
                _("Reporting issues in public spaces"),
                _("Location-based wishes and improvement suggestions"),
                _("Identifying local resources or infrastructure needs"),
            ],
        },
    ]

    return render(
        request,
        "landing.html",
        {
            "statistics_columns": zip(columns, directions),
            "statistics_rows_mobile": zip(mobile_rows, directions),
            "contact_form_page": contact_form_page,
            "contact_form": contact_form,
            "news": news_block,
            "faq_page": faq_page,
            "modules": modules,
        },
    )

import random

from django.shortcuts import render

from apps.cms.contacts.models import FormPage
from apps.cms.news.models import NewsIndexPage

from .models import StatisticsItem


def landing_view(request):
    items = list(StatisticsItem.objects.all().order_by("order"))
    random.shuffle(items)

    # contact form
    form_page = FormPage.objects.get(slug="contact").specific

    # news articles
    news_index = NewsIndexPage.objects.live().first()
    latest_news = news_index.news[:3] if news_index else []
    news_block = {"news_page": news_index, "latest_news": latest_news}

    # Split statistics into 4 columns
    columns = [items[i::4] for i in range(4)]
    # Alternate directions: down, up, down, up
    directions = ["down", "up", "down", "up"]

    return render(
        request,
        "landing.html",
        {
            "statistics_columns": zip(columns, directions),
            "contact_form_page": form_page,
            "news": news_block,
        },
    )

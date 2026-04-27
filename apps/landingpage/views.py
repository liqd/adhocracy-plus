import random

from django.shortcuts import render

from apps.cms.contacts.models import FormPage
from apps.cms.news.models import NewsIndexPage
from apps.cms.pages.models import SimplePage

from .models import StatisticsItem


def landing_view(request):
    # Get statistics
    items = list(StatisticsItem.objects.all().order_by("order"))
    random.shuffle(items)

    # Contact form (safe)
    form_page = FormPage.objects.filter(slug="contact").first()
    if form_page:
        form_page = form_page.specific

    # News articles
    news_index = NewsIndexPage.objects.live().first()
    if news_index:
        latest_news = news_index.news[:3]
        news_block = {"news_page": news_index, "latest_news": latest_news}
    else:
        news_block = None

    # FAQ page
    faq_page = SimplePage.objects.live().filter(slug="initiatorguide").first()

    # Split statistics
    columns = [items[i::4] for i in range(4)]
    directions = ["down", "up", "down", "up"]

    return render(
        request,
        "landing.html",
        {
            "statistics_columns": zip(columns, directions),
            "contact_form_page": form_page,
            "news": news_block,
            "faq_page": faq_page,
        },
    )

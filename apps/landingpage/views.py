import random

from django.shortcuts import render

from .models import StatisticsItem


def landing_view(request):
    items = list(StatisticsItem.objects.all())
    random.shuffle(items)
    return render(request, "landing.html", {"stats": items})

import random

from django.shortcuts import render

from .models import StatisticsItem


def landing_view(request):
    items = list(StatisticsItem.objects.all().order_by("order"))
    random.shuffle(items)

    # Split into 4 columns
    columns = [items[i::4] for i in range(4)]
    # Alternate directions: down, up, down, up
    directions = ["down", "up", "down", "up"]

    return render(request, "landing.html", {"columns": zip(columns, directions)})

from django.urls import path

from .views import ChoinEventListView
from .views import accepted_ideas
from .views import ideas_fair_acceptance_order

urlpatterns = [
    path("choinevents/", ChoinEventListView.as_view(), name="choinevent-list"),
    path("accepted_idea_list/<int:obj_id>/", accepted_ideas, name="accepted_ideas"),
    path(
        "fair_acceptance_order/<int:obj_id>/",
        ideas_fair_acceptance_order,
        name="fair_acceptance_order",
    ),
]

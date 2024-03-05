from django.urls import path

from .views import ChoinEventListView
from .views import accepted_ideas

urlpatterns = [
    path("choinevents/", ChoinEventListView.as_view(), name="choinevent-list"),
    path("accepted_idea_list/<int:obj_id>/", accepted_ideas, name="accepted_ideas"),
]

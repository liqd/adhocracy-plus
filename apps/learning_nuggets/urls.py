from django.urls import re_path

from .views import LearningCategoryView
from .views import LearningCenterView
from .views import LearningNuggetView

app_name = "learning_nuggets"

urlpatterns = [
    re_path(
        r"^$",
        LearningCenterView.as_view(),
        name="index",
    ),
    re_path(
        r"^(?P<category_slug>[-\w_]+)/$",
        LearningCategoryView.as_view(),
        name="category",
    ),
    re_path(
        r"^(?P<category_slug>[-\w_]+)/(?P<nugget_slug>[-\w_]+)/$",
        LearningNuggetView.as_view(),
        name="nugget-detail",
    ),
]

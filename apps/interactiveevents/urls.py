from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'present/module/(?P<module_slug>[-\w_]+)/$',
        views.LiveQuestionPresentationListView.as_view(),
        name='question-present'),
    url(r'(?P<module_slug>[-\w_]+)/$',
        views.LiveQuestionModuleDetail.as_view(),
        name='live-question-module-detail'),
]

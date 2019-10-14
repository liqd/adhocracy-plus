from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'create/module/(?P<slug>[-\w_]+)/$',
        views.QuestionCreateView.as_view(), name='question-create'),
    url(r'present/module/(?P<module_slug>[-\w_]+)/$',
        views.QuestionPresentationListView.as_view(), name='question-present'),
]

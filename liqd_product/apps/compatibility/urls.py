from django.conf.urls import url
from django.http import Http404


def not_found_view(request, *args, **kwargs):
    raise Http404('Not available in _LIQD PRODUCT_ yet.')


urlpatterns = [
    url(r'^projects/(?P<slug>[-\w_]+)/$',
        not_found_view,
        name='dashboard-project-edit'),
]

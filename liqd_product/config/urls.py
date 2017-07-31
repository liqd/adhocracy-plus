"""_LIQD_PRODUCT_ URL Configuration."""

from ckeditor_uploader import views as ck_views
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.views.i18n import javascript_catalog
from rest_framework import routers

from adhocracy4.api import routers as a4routers
from adhocracy4.comments.api import CommentViewSet
from adhocracy4.follows.api import FollowViewSet
from adhocracy4.ratings.api import RatingViewSet
from adhocracy4.reports.api import ReportViewSet
from liqd_product.apps.partners.urlresolvers import partner_patterns
from liqd_product.apps.users.decorators import user_is_project_admin

js_info_dict = {
    'packages': ('adhocracy4.comments',),
}

router = routers.DefaultRouter()
router.register(r'follows', FollowViewSet, base_name='follows')
router.register(r'reports', ReportViewSet, base_name='reports')

module_router = a4routers.ModuleDefaultRouter()

orga_router = a4routers.OrganisationDefaultRouter()

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r'comments', CommentViewSet, base_name='comments')
ct_router.register(r'ratings', RatingViewSet, base_name='ratings')


urlpatterns = [
    # General platform urls
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^account/', include('liqd_product.apps.account.urls')),
    url(r'^embed/', include('meinberlin.apps.embed.urls')),
    url(r'^exports/', include('meinberlin.apps.exports.urls')),

    # Urls within the context of a partner
    partner_patterns(
        url(r'^projects/', include('adhocracy4.projects.urls')),
        url(r'^ideas/', include(r'meinberlin.apps.ideas.urls',
                                namespace='meinberlin_ideas')),
        url(r'^$', include('liqd_product.apps.partners.urls'))
    ),

    # API urls
    url(r'^api/', include(ct_router.urls)),
    url(r'^api/', include(module_router.urls)),
    url(r'^api/', include(orga_router.urls)),
    url(r'^api/', include(router.urls)),

    url(r'^upload/', user_is_project_admin(ck_views.upload),
        name='ckeditor_upload'),
    url(r'^browse/', never_cache(user_is_project_admin(ck_views.browse)),
        name='ckeditor_browse'),

    url(r'^jsi18n/$', javascript_catalog,
        js_info_dict, name='javascript-catalog'),

    # Temporary Compatibility layer for a4-meinberlin
    url(r'^missing/', include('liqd_product.apps.compatibility.urls')),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media locally
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

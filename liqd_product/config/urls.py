"""Beteiligung.in URL Configuration."""

from ckeditor_uploader import views as ck_views
from django.conf import settings
from django.conf.urls import i18n
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from rest_framework import routers
from wagtail.contrib.sitemaps import views as wagtail_sitemap_views
from wagtail.contrib.sitemaps.sitemap_generator import \
    Sitemap as WagtailSitemap

from adhocracy4.api import routers as a4routers
from adhocracy4.comments.api import CommentViewSet
from adhocracy4.follows.api import FollowViewSet
from adhocracy4.ratings.api import RatingViewSet
from adhocracy4.reports.api import ReportViewSet
from apps.contrib import views as contrib_views
from apps.contrib.sitemaps.product_partners_sitemap import \
    ProductPartnersSitemap
from apps.contrib.sitemaps.product_projects_sitemap import \
    ProductProjectsSitemap
from apps.contrib.sitemaps.static_sitemap import StaticSitemap
from apps.documents.api import DocumentViewSet
from apps.moderatorremark.api import ModeratorRemarkViewSet
from apps.partners.urlresolvers import partner_patterns
from apps.polls.api import PollViewSet
from apps.polls.api import VoteViewSet
from apps.polls.routers import QuestionDefaultRouter
from apps.users.decorators import user_is_project_admin

router = routers.DefaultRouter()
router.register(r'follows', FollowViewSet, base_name='follows')
router.register(r'reports', ReportViewSet, base_name='reports')
router.register(r'polls', PollViewSet, base_name='polls')

module_router = a4routers.ModuleDefaultRouter()
# FIXME: rename to 'chapters'
module_router.register(r'documents', DocumentViewSet, base_name='chapters')

orga_router = a4routers.OrganisationDefaultRouter()

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r'comments', CommentViewSet, base_name='comments')
ct_router.register(r'ratings', RatingViewSet, base_name='ratings')
ct_router.register(r'moderatorremarks', ModeratorRemarkViewSet,
                   base_name='moderatorremarks')

question_router = QuestionDefaultRouter()
question_router.register(r'vote', VoteViewSet, base_name='vote')

sitemaps = {
    'partners': ProductPartnersSitemap,
    'projects': ProductProjectsSitemap,
    'wagtail': WagtailSitemap,
    'static': StaticSitemap
}

urlpatterns = [
    # General platform urls
    url(r'^django-admin/', admin.site.urls),
    url(r'^admin/', include('wagtail.admin.urls')),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^account/', include('apps.account.urls')),
    url(r'^dashboard/', include('apps.dashboard.urls')),
    url(r'^embed/', include('apps.embed.urls')),
    url(r'^profile/', include('apps.users.urls')),
    url(r'^i18n/', include(i18n)),

    # API urls
    url(r'^api/', include(ct_router.urls)),
    url(r'^api/', include(module_router.urls)),
    url(r'^api/', include(orga_router.urls)),
    url(r'^api/', include(question_router.urls)),
    url(r'^api/', include(router.urls)),

    url(r'^upload/', user_is_project_admin(ck_views.upload),
        name='ckeditor_upload'),
    url(r'^browse/', never_cache(user_is_project_admin(ck_views.browse)),
        name='ckeditor_browse'),

    url(r'^components/$', contrib_views.ComponentLibraryView.as_view()),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    # Urls within the context of a partner
    partner_patterns(
        url(r'^modules/', include('adhocracy4.modules.urls')),
        # Temporary include liqd_product projects urls, as they contain
        # the invite links. This may be removed when invites are refactored
        # to a separate app.
        url(r'^projects/', include('apps.projects.urls')),
        url(r'^offlineevents/', include(
            ('apps.offlineevents.urls', 'a4_candy_offlineevents'),
            namespace='a4_candy_offlineevents')),
        url(r'^ideas/', include(('apps.ideas.urls', 'a4_candy_ideas'),
                                namespace='a4_candy_ideas')),
        url(r'^mapideas/', include(('apps.mapideas.urls', 'a4_candy_mapideas'),
                                   namespace='a4_candy_mapideas')),
        url(r'^text/', include(('apps.documents.urls', 'a4_candy_documents'),
                               namespace='a4_candy_documents')),
        url(r'^budgeting/', include(('apps.budgeting.urls',
                                     'a4_candy_budgeting'),
                                    namespace='a4_candy_budgeting')),
    ),

    url(r'^sitemap\.xml$', wagtail_sitemap_views.index,
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'^sitemap-(?P<section>.+)\.xml$', wagtail_sitemap_views.sitemap,
        {'sitemaps': sitemaps}, name='sitemaps'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
        content_type="text/plain"), name="robots_file"),

    url(r'', include('apps.partners.urls')),
    url(r'', include('wagtail.core.urls'))
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

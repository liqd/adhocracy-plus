"""adhocracy+ URL Configuration."""

from django.conf import settings
from django.conf.urls import i18n
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.defaults import server_error
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from django_ckeditor_5 import views as ckeditor5_views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap
from wagtail.documents import urls as wagtaildocs_urls

from adhocracy4.api import routers as a4routers
from adhocracy4.comments.api import CommentModerateSet
from adhocracy4.follows.api import FollowViewSet
from adhocracy4.polls.api import PollViewSet
from adhocracy4.ratings.api import RatingViewSet
from adhocracy4.reports.api import ReportViewSet
from apps.account.api import AccountViewSet
from apps.contrib import views as contrib_views
from apps.contrib.sitemaps import static_sitemap_index
from apps.documents.api import DocumentViewSet
from apps.ideas.api import IdeaViewSet
from apps.interactiveevents.api import LikesViewSet
from apps.interactiveevents.api import LiveQuestionViewSet
from apps.interactiveevents.routers import LikesDefaultRouter
from apps.moderatorfeedback.api import CommentWithFeedbackViewSet
from apps.moderatorfeedback.api import ModeratorCommentFeedbackViewSet
from apps.moderatorremark.api import ModeratorRemarkViewSet
from apps.organisations.sitemaps import organisations_sitemap_index
from apps.projects.api import AppModuleViewSet
from apps.projects.api import AppProjectsViewSet
from apps.projects.api import ModerationProjectsViewSet
from apps.userdashboard.api import ModerationCommentViewSet
from apps.userdashboard.routers import ModerationDetailDefaultRouter
from apps.users.api import UserViewSet
from apps.users.decorators import user_is_project_admin
from apps.users.views import set_language_overwrite

router = routers.DefaultRouter()
router.register(r"follows", FollowViewSet, basename="follows")
router.register(r"reports", ReportViewSet, basename="reports")
router.register(r"polls", PollViewSet, basename="polls")
router.register(r"app-projects", AppProjectsViewSet, basename="app-projects")
router.register(r"app-modules", AppModuleViewSet, basename="app-modules")
router.register(r"users", UserViewSet, basename="users")
router.register(
    r"moderationprojects", ModerationProjectsViewSet, basename="moderationprojects"
)


module_router = a4routers.ModuleDefaultRouter()
# FIXME: rename to 'chapters'
module_router.register(r"documents", DocumentViewSet, basename="chapters")
module_router.register(
    r"interactiveevents/livequestions",
    LiveQuestionViewSet,
    basename="interactiveevents",
)
module_router.register(r"ideas", IdeaViewSet, basename="ideas")

likes_router = LikesDefaultRouter()
likes_router.register(r"likes", LikesViewSet, basename="likes")

moderation_router = ModerationDetailDefaultRouter()
moderation_router.register(
    r"comments", ModerationCommentViewSet, basename="moderationcomments"
)

orga_router = a4routers.OrganisationDefaultRouter()

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r"comments", CommentWithFeedbackViewSet, basename="comments")
ct_router.register(r"ratings", RatingViewSet, basename="ratings")
ct_router.register(
    r"moderatorremarks", ModeratorRemarkViewSet, basename="moderatorremarks"
)
ct_router.register(r"comment-moderate", CommentModerateSet, basename="comment-moderate")

comment_router = a4routers.CommentDefaultRouter()
comment_router.register(
    r"moderatorfeedback", ModeratorCommentFeedbackViewSet, basename="moderatorfeedback"
)

urlpatterns = [
    # General platform urls
    re_path(r"^django-admin/", admin.site.urls),
    path("admin/", include("wagtail.admin.urls")),
    path("documents/", include(wagtaildocs_urls)),
    path("accounts/", include("allauth.urls")),
    path("account/", include("apps.account.urls")),
    path("profile/", include("apps.users.urls")),
    path("userdashboard/", include("apps.userdashboard.urls")),
    # this needs to be above i18n/ to make the overwrite work
    path("i18n/setlang/", set_language_overwrite, name="set_language"),
    path("i18n/", include(i18n)),
    # API urls
    path("api/", include(ct_router.urls)),
    path("api/", include(module_router.urls)),
    path("api/", include(orga_router.urls)),
    path("api/", include(likes_router.urls)),
    path("api/", include(comment_router.urls)),
    path("api/", include(moderation_router.urls)),
    path("api/", include(router.urls)),
    re_path(r"^api/account/", AccountViewSet.as_view(), name="api-account"),
    # API JWT authentication
    re_path(r"^api/login", obtain_auth_token, name="api-login"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_jwt"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "ckeditor5/image_upload/",
        user_is_project_admin(ckeditor5_views.upload_file),
        name="ck_editor_5_upload_file",
    ),
    path("components/", contrib_views.ComponentLibraryView.as_view()),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    re_path(
        r"^(?P<organisation_slug>[-\w_]+)/",
        include(
            [
                path(
                    "budgeting/",
                    include(
                        ("apps.budgeting.urls", "a4_candy_budgeting"),
                        namespace="a4_candy_budgeting",
                    ),
                ),
                path("dashboard/", include("apps.dashboard.urls")),
                path(
                    "ideas/",
                    include(
                        ("apps.ideas.urls", "a4_candy_ideas"),
                        namespace="a4_candy_ideas",
                    ),
                ),
                path(
                    "mapideas/",
                    include(
                        ("apps.mapideas.urls", "a4_candy_mapideas"),
                        namespace="a4_candy_mapideas",
                    ),
                ),
                path(
                    "offlineevents/",
                    include(
                        ("apps.offlineevents.urls", "a4_candy_offlineevents"),
                        namespace="a4_candy_offlineevents",
                    ),
                ),
                path("projects/", include("apps.projects.urls")),
                path("interactiveevents/", include("apps.interactiveevents.urls")),
                path(
                    "text/",
                    include(
                        ("apps.documents.urls", "a4_candy_documents"),
                        namespace="a4_candy_documents",
                    ),
                ),
                path(
                    "topicprio/",
                    include(
                        ("apps.topicprio.urls", "a4_candy_topicprio"),
                        namespace="a4_candy_topicprio",
                    ),
                ),
                path(
                    "subjects/",
                    include(
                        ("apps.debate.urls", "a4_candy_debate"),
                        namespace="a4_candy_debate",
                    ),
                ),
            ]
        ),
    ),
    path("sitemap.xml", static_sitemap_index, name="static-sitemap-index"),
    path("sitemap-wagtail.xml", wagtail_sitemap, name="wagtail-sitemap"),
    path(
        "sitemap-organisations.xml",
        organisations_sitemap_index,
        name="organisations-sitemap-index",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_file",
    ),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += [
        path("403/", TemplateView.as_view(template_name="403.html")),
        path("404/", TemplateView.as_view(template_name="404.html")),
        path("500/", server_error),
    ]

    # Serve static and media locally
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns


# generic patterns at the very end
urlpatterns += [
    path("", include("apps.organisations.urls")),
    path("", include("wagtail.urls")),
]

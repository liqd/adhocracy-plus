"""adhocracy+ URL Configuration."""

from django.conf import settings
from django.conf.urls import i18n
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.defaults import server_error
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog
from django_ckeditor_5 import views as ckeditor5_views
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
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
from apps.fairvote.api import ChoinViewSet
from apps.fairvote.api import IdeaChoinViewSet
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
router.register(r"choins", ChoinViewSet, basename="choins")
router.register(r"idea-choins", IdeaChoinViewSet, basename="idea-choins")


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
    re_path(
        r"^django-admin/", admin.site.urls
    ),  # https://aplus.csariel.xyz/django-admin/
    path("admin/", include("wagtail.admin.urls")),  # https://aplus.csariel.xyz/admin/
    path(
        "documents/", include(wagtaildocs_urls)
    ),  # https://aplus.csariel.xyz/admin/documents/ ?
    path(
        "accounts/", include("allauth.urls")
    ),  # https://github.com/pennersr/django-allauth/blob/main/allauth/urls.py
    # https://aplus.csariel.xyz/accounts/login/   # https://github.com/pennersr/django-allauth/blob/main/allauth/account/urls.py
    # https://aplus.csariel.xyz/accounts/logout/
    # https://aplus.csariel.xyz/accounts/inactive/
    path("account/", include("apps.account.urls")),
    # https://aplus.csariel.xyz/account
    # https://aplus.csariel.xyz/account/profile
    path("profile/", include("apps.users.urls")),
    path(
        "userdashboard/", include("apps.userdashboard.urls")
    ),  # https://aplus.csariel.xyz/userdashboard/overview/
    path("i18n/", include(i18n)),
    # API urls
    path("api/", include(ct_router.urls)),
    path("api/", include(module_router.urls)),
    path("api/", include(orga_router.urls)),
    path("api/", include(likes_router.urls)),
    path("api/", include(comment_router.urls)),
    path("api/", include(moderation_router.urls)),
    path("api/", include(router.urls)),
    re_path(r"^api/login", obtain_auth_token, name="api-login"),
    re_path(r"^api/account/", AccountViewSet.as_view(), name="api-account"),
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
                path("fairvote/", include("apps.fairvote.urls")),
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
    path(
        "sitemap.xml", static_sitemap_index, name="static-sitemap-index"
    ),  # https://aplus.csariel.xyz/sitemap.xml
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


class HomePageView(RedirectView):
    permanent = False
    pattern_name = "accounts_login"  # redirect home page to accounts/login


# generic patterns at the very end
urlpatterns += [
    path("", include("apps.organisations.urls")),  # /<organization_slug>/
    # path("", include("wagtail.urls")),             # /
    # https://aplus.csariel.xyz/_util/login/
    path("", HomePageView.as_view()),  # /
]

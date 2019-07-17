from django.conf.urls import url

from adhocracy4.projects.urls import urlpatterns as a4_projects_urls

from . import views

urlpatterns = [
    url(r'^participant-invites/(?P<invite_token>[-\w_]+)/$',
        views.ParticipantInviteDetailView.as_view(),
        name='project-participant-invite-detail'),
    url(r'^project-delete/(?P<pk>[-\w_]+)/$',
        views.ProjectDeleteView.as_view(),
        name='project-delete'),
    url(r'^participant-invites/(?P<invite_token>[-\w_]+)/accept/$',
        views.ParticipantInviteUpdateView.as_view(),
        name='project-participant-invite-update'),
    url(r'^moderator-invites/(?P<invite_token>[-\w_]+)/$',
        views.ModeratorInviteDetailView.as_view(),
        name='project-moderator-invite-detail'),
    url(r'^moderator-invites/(?P<invite_token>[-\w_]+)/accept/$',
        views.ModeratorInviteUpdateView.as_view(),
        name='project-moderator-invite-update'),
    url(r'^(?P<slug>[-\w_]+)/$', views.ProjectDetailView.as_view(),
        name='project-detail'),
    url(r'^module/(?P<module_slug>[-\w_]+)/$',
        views.ModuleDetailView.as_view(),
        name='module-detail')
]

urlpatterns += a4_projects_urls

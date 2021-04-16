from rest_framework import routers

from adhocracy4.api.routers import CustomRouterMixin


class ModerationDetailRouterMixin(CustomRouterMixin):

    prefix_regex = (
        r'userdashboard/moderation/(?P<project_pk>[\d]+)/{prefix}'
    )


class ModerationDetailDefaultRouter(ModerationDetailRouterMixin,
                                    routers.DefaultRouter):
    pass

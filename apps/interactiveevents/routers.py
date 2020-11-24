from rest_framework import routers

from adhocracy4.api.routers import CustomRouterMixin


class LikesRouterMixin(CustomRouterMixin):

    prefix_regex = (
        r'livequestions/(?P<livequestion_pk>[\d]+)/{prefix}'
    )


class LikesDefaultRouter(LikesRouterMixin, routers.DefaultRouter):
    pass

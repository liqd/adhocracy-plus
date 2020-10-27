from django.db.models import Q

from adhocracy4.projects.enums import Access


def filter_viewable(queryset, user):
    # FIXME: has to be in sync with a4projects.view_project or here
    #        a4projects.view_project and should
    #        be implemented on the Project's QueryManager/QuerySet.
    #        Unfortunately that is not possible, as the QueryManager may not
    #        be overwritten and the Project model is not swappable.
    if user.is_superuser:
        return queryset
    elif user.is_authenticated:
        return queryset.filter(
            Q(access=Access.PUBLIC) |
            Q(access=Access.SEMIPUBLIC) |
            Q(participants__in=[user.id]) |
            Q(organisation__initiators__id__in=[user.id]) |
            Q(moderators__in=[user.id]) |
            Q(organisation__member__member__id=user.id)
        ).distinct()
    else:
        return queryset.filter(
            Q(access=Access.PUBLIC) |
            Q(access=Access.SEMIPUBLIC)
        )

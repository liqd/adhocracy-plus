from django.utils.translation import gettext as _
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from adhocracy4.api.mixins import ModuleMixin
from adhocracy4.api.permissions import ViewSetRulesPermission
from adhocracy4.phases import predicates as phase_predicates

from apps.ideas.models import Idea

from .models import RankedBallot
from .serializers import RankedBallotSerializer


class RankedBallotViewSet(
    ModuleMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Module-scoped endpoint to upsert the current user's ranked ballot.

    A single ballot per user and module is kept.
    """

    serializer_class = RankedBallotSerializer
    permission_classes = (ViewSetRulesPermission,)

    @property
    def rules_method_map(self):
        default = ViewSetRulesPermission.default_rules_method_map
        return default._replace(
            POST="a4_candy_ranked_choice.rank_idea",
        )

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        return RankedBallot.objects.filter(module=self.module).prefetch_related(
            "entries"
        )

    def create(self, request, *args, **kwargs):
        if not phase_predicates.has_feature_active(self.module, Idea, "rank"):
            # Superusers bypass the rules framework via ModelBackend, so the
            # active-phase check is enforced here explicitly.
            raise PermissionDenied(_("The ranking phase is over."))
        # Upsert: a user can only ever have one ballot per module.
        RankedBallot.objects.filter(module=self.module, creator=request.user).delete()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
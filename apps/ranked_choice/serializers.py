from django.utils.translation import gettext as _
from rest_framework import serializers

from apps.ideas.models import Idea

from .models import RankedBallot
from .models import RankedEntry


class RankedBallotSerializer(serializers.Serializer):
    """Serialize a ballot with its ranked idea pks (ordered by preference).

    ``ranks`` is write-only on input (an ordered list of idea pks) and rendered
    back from the stored entries on output.
    """

    id = serializers.ReadOnlyField()
    module = serializers.IntegerField(read_only=True, source="module_id")
    ranks = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    def validate(self, attrs):
        ranks = attrs.get("ranks")
        if not ranks:
            raise serializers.ValidationError(_("Please rank at least one idea."))

        if len(ranks) != len(set(ranks)):
            raise serializers.ValidationError(_("Ranks must not contain duplicates."))

        module = self.context["view"].module
        ideas = list(Idea.objects.filter(module=module, pk__in=ranks))
        if len(ideas) != len(ranks):
            raise serializers.ValidationError(
                _("All ranked ideas must belong to the current module.")
            )

        attrs["_ideas"] = {idea.pk: idea for idea in ideas}
        return attrs

    def create(self, validated_data):
        module = self.context["view"].module
        creator = self.context["request"].user
        ballot = RankedBallot.objects.create(module=module, creator=creator)
        self._set_ranks(ballot, validated_data)
        return ballot

    def update(self, instance, validated_data):
        instance.entries.all().delete()
        self._set_ranks(instance, validated_data)
        instance.save()
        return instance

    def _set_ranks(self, ballot, validated_data):
        ranks = validated_data["ranks"]
        ideas_by_pk = validated_data["_ideas"]
        entries = [
            RankedEntry(
                ballot=ballot,
                content_object=ideas_by_pk[pk],
                rank=offset + 1,
            )
            for offset, pk in enumerate(ranks)
        ]
        RankedEntry.objects.bulk_create(entries)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["ranks"] = list(
            instance.entries.order_by("rank", "id").values_list("object_pk", flat=True)
        )
        return data
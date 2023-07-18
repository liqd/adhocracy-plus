from functools import lru_cache

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from adhocracy4.api.dates import get_date_display
from adhocracy4.api.dates import get_datetime_display
from adhocracy4.categories.models import Category
from adhocracy4.labels.models import Label
from adhocracy4.modules.models import Module
from adhocracy4.phases.models import Phase
from adhocracy4.projects.models import Project
from apps.projects import helpers


class AppProjectSerializer(serializers.ModelSerializer):
    information = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    # todo: remove many=True once AppProjects are restricted to single module
    published_modules = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    organisation = serializers.SerializerMethodField()
    organisation_logo = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()
    single_idea_collection_module = serializers.SerializerMethodField()
    single_poll_module = serializers.SerializerMethodField()
    participation_time_display = serializers.SerializerMethodField()
    has_contact_info = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "pk",
            "name",
            "description",
            "information",
            "result",
            "organisation",
            "organisation_logo",
            "published_modules",
            "access",
            "image",
            "single_idea_collection_module",
            "single_poll_module",
            "participation_time_display",
            "module_running_progress",
            "has_contact_info",
            "contact_name",
            "contact_address_text",
            "contact_phone",
            "contact_email",
            "contact_url",
        )

    def get_information(self, project):
        return project.information.strip()

    def get_result(self, project):
        return project.result.strip()

    def get_organisation(self, project):
        if project.organisation.title:
            return project.organisation.title
        else:
            return project.organisation.name

    def get_organisation_logo(self, project):
        if project.organisation.logo:
            return project.organisation.logo.url
        return None

    def get_access(self, project):
        return project.access.name

    def get_single_idea_collection_module(self, project):
        if (
            project.published_modules.count() == 1
            and project.published_modules.first().blueprint_type == "IC"
        ):
            return project.published_modules.first().pk
        return False

    def get_single_poll_module(self, project):
        if (
            project.published_modules.count() == 1
            and project.published_modules.first().blueprint_type == "PO"
        ):
            return project.published_modules.first().pk
        return False

    def get_participation_time_display(self, project):
        if project.running_modules:
            if project.module_running_days_left < 365:
                return _("%(time_left)s remaining") % {
                    "time_left": project.module_running_time_left
                }
            else:
                return _("more than 1 year remaining")
        elif project.future_modules:
            return _("Participation: from %(project_start)s") % {
                "project_start": get_date_display(
                    project.future_modules.first().module_start
                )
            }
        elif project.past_modules:
            return _("Participation ended. Read result.")
        return ""

    def get_has_contact_info(self, project):
        if (
            project.contact_name
            or project.contact_address_text
            or project.contact_phone
            or project.contact_email
            or project.contact_url
        ):
            return True
        return False


class AppPhaseSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = Phase
        fields = ("name", "description", "type", "start_date", "end_date")

    def get_start_date(self, phase):
        return get_datetime_display(phase.start_date)

    def get_end_date(self, phase):
        return get_datetime_display(phase.end_date)


class AppModuleSerializer(serializers.ModelSerializer):
    active_phase = serializers.SerializerMethodField()
    future_phases = serializers.SerializerMethodField()
    past_phases = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    has_idea_adding_permission = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = (
            "pk",
            "active_phase",
            "future_phases",
            "past_phases",
            "labels",
            "categories",
            "has_idea_adding_permission",
        )

    def get_active_phase(self, module):
        if module.active_phase:
            serializer = AppPhaseSerializer(instance=module.active_phase)
            return serializer.data
        return None

    def get_future_phases(self, module):
        if module.future_phases:
            serializer = AppPhaseSerializer(instance=module.future_phases, many=True)
            return serializer.data
        return None

    def get_past_phases(self, module):
        if module.past_phases:
            serializer = AppPhaseSerializer(instance=module.past_phases, many=True)
            return serializer.data
        return None

    def get_labels(self, instance):
        labels = Label.objects.filter(module=instance)
        if labels:
            return [{"id": label.pk, "name": label.name} for label in labels]
        return False

    def get_categories(self, instance):
        categories = Category.objects.filter(module=instance)
        if categories:
            return [
                {"id": category.pk, "name": category.name} for category in categories
            ]
        return False

    def get_has_idea_adding_permission(self, instance):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return user.has_perm("a4_candy_ideas.add_idea", instance)
        return False


class ModerationProjectSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    tile_image = serializers.SerializerMethodField()
    tile_image_copyright = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    participation_active = serializers.SerializerMethodField()
    participation_string = serializers.SerializerMethodField()
    future_phase = serializers.SerializerMethodField()
    active_phase = serializers.SerializerMethodField()
    past_phase = serializers.SerializerMethodField()
    num_reported_unread_comments = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    moderation_detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "title",
            "organisation",
            "tile_image",
            "tile_image_alt_text",
            "tile_image_copyright",
            "status",
            "access",
            "participation_active",
            "participation_string",
            "future_phase",
            "active_phase",
            "past_phase",
            "num_reported_unread_comments",
            "comment_count",
            "moderation_detail_url",
        ]

    @lru_cache(maxsize=1)
    def _get_participation_status_project(self, instance):
        project_phases = instance.phases

        if project_phases.active_phases():
            return _("running"), True

        if project_phases.future_phases():
            try:
                return (
                    _("starts on {}").format(
                        project_phases.future_phases()
                        .first()
                        .start_date.strftime("%d.%m.%y")
                    ),
                    True,
                )
            except AttributeError:
                return (_("starts in the future"), True)
        else:
            return _("completed"), False

    def get_type(self, instance):
        return "project"

    def get_title(self, instance):
        return instance.name

    def get_organisation(self, instance):
        return instance.organisation.name

    def get_tile_image(self, instance):
        image_url = ""
        if instance.tile_image:
            image = get_thumbnailer(instance.tile_image)["project_thumbnail"]
            image_url = image.url
        elif instance.image:
            image = get_thumbnailer(instance.image)["project_thumbnail"]
            image_url = image.url
        return image_url

    def get_tile_image_alt_text(self, instance):
        if instance.tile_image:
            return instance.tile_image_alt_text
        elif instance.image:
            return instance.image_alt_text
        else:
            return None

    def get_tile_image_copyright(self, instance):
        if instance.tile_image:
            return instance.tile_image_copyright
        elif instance.image:
            return instance.image_copyright
        else:
            return None

    def get_status(self, instance):
        project_phases = instance.phases
        if project_phases.active_phases() or project_phases.future_phases():
            return 0
        return 1

    def get_participation_active(self, instance):
        (
            participation_string,
            participation_active,
        ) = self._get_participation_status_project(instance)
        return participation_active

    def get_participation_string(self, instance):
        (
            participation_string,
            participation_active,
        ) = self._get_participation_status_project(instance)
        return str(participation_string)

    def get_future_phase(self, instance):
        if instance.future_modules and instance.future_modules.first().module_start:
            return str(instance.future_modules.first().module_start)
        return False

    def get_active_phase(self, instance):
        if instance.active_phase_ends_next:
            progress = instance.module_running_progress
            time_left = instance.module_running_time_left
            end_date = str(instance.running_module_ends_next.module_end)
            return [progress, time_left, end_date]
        return False

    def get_past_phase(self, instance):
        if instance.past_modules and instance.past_modules.first().module_end:
            return str(instance.past_modules.first().module_end)
        return False

    def get_num_reported_unread_comments(self, instance):
        return helpers.get_num_reported_unread_comments(instance)

    def get_comment_count(self, instance):
        return helpers.get_num_comments_project(instance)

    def get_moderation_detail_url(self, instance):
        return reverse(
            "userdashboard-moderation-detail", kwargs={"slug": instance.slug}
        )

from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from adhocracy4.categories.models import Category
from adhocracy4.labels.models import Label
from adhocracy4.modules.models import Module
from adhocracy4.phases.models import Phase
from adhocracy4.projects.models import Project


class AppProjectSerializer(serializers.ModelSerializer):

    information = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    # todo: remove many=True once AppProjects are restricted to single module
    published_modules = serializers.PrimaryKeyRelatedField(read_only=True,
                                                           many=True)
    organisation = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()
    single_agenda_setting_module = serializers.SerializerMethodField()
    single_poll_module = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('pk', 'name', 'description', 'information', 'result',
                  'organisation', 'published_modules', 'access', 'image',
                  'single_agenda_setting_module', 'single_poll_module')

    def get_information(self, project):
        return strip_tags(project.information)

    def get_result(self, project):
        return strip_tags(project.result)

    def get_organisation(self, project):
        return project.organisation.name

    def get_access(self, project):
        return project.access.name

    # todo: module logic has to be replaced once we introduced module types
    # currently only works because agenda setting is only module using phase
    # of type 'a4_candy_ideas:rating'
    def get_single_agenda_setting_module(self, project):
        if (project.published_modules.count() == 1 and
                any([True for phase in project.modules.first().phases
                    if phase.type == 'a4_candy_ideas:rating'])):
            return project.published_modules.first().pk
        return False

    def get_single_poll_module(self, project):
        if (project.published_modules.count() == 1 and
                project.published_modules.first().phases.count() == 1 and
                project.published_modules.first().phases.first().type
                == 'a4_candy_polls:voting'):
            return project.published_modules.first().pk
        return False


class AppPhaseSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Phase
        fields = ('name', 'description', 'type', 'start_date',
                  'end_date', 'is_active')

    def get_is_active(self, instance):
        if instance.start_date and instance.end_date:
            return (instance.start_date <= timezone.now()
                    and instance.end_date >= timezone.now())
        return False


class AppModuleSerializer(serializers.ModelSerializer):
    phases = AppPhaseSerializer(many=True, read_only=True)
    labels = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    ideas_collect_phase_active = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ('pk', 'phases', 'labels', 'categories',
                  'ideas_collect_phase_active')

    def get_labels(self, instance):
        labels = Label.objects.filter(module=instance)
        if labels:
            return [(label.pk, label.name) for label in labels]
        return False

    def get_categories(self, instance):
        categories = Category.objects.filter(module=instance)
        if categories:
            return [(category.pk, category.name) for category in categories]
        return False

    def get_ideas_collect_phase_active(self, instance):
        if instance.phases:
            for phase in instance.phases:
                if phase.start_date and phase.end_date:
                    if (phase.type == 'a4_candy_ideas:collect'
                            and phase.start_date <= timezone.now()
                            and phase.end_date >= timezone.now()):
                        return True
        return False

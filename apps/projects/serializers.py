from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from adhocracy4.api.dates import get_date_display
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
    organisation_logo = serializers.SerializerMethodField()
    access = serializers.SerializerMethodField()
    single_idea_collection_module = serializers.SerializerMethodField()
    single_poll_module = serializers.SerializerMethodField()
    participation_time_display = serializers.SerializerMethodField()
    has_contact_info = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('pk', 'name', 'description', 'information', 'result',
                  'organisation', 'organisation_logo', 'published_modules',
                  'access', 'image', 'single_idea_collection_module',
                  'single_poll_module', 'participation_time_display',
                  'module_running_progress', 'has_contact_info',
                  'contact_name', 'contact_address_text', 'contact_phone',
                  'contact_email', 'contact_url')

    def get_information(self, project):
        return project.information.strip()

    def get_result(self, project):
        return project.result.strip()

    def get_organisation(self, project):
        return project.organisation.name

    def get_organisation_logo(self, project):
        if project.organisation.logo:
            return project.organisation.logo.url
        return None

    def get_access(self, project):
        return project.access.name

    def get_single_idea_collection_module(self, project):
        if project.published_modules.count() == 1 and \
                project.published_modules.first().blueprint_type == 'IC':
            return project.published_modules.first().pk
        return False

    def get_single_poll_module(self, project):
        if project.published_modules.count() == 1 and \
                project.published_modules.first().blueprint_type == 'PO':
            return project.published_modules.first().pk
        return False

    def get_participation_time_display(self, project):
        if project.running_modules:
            if project.module_running_days_left < 365:
                return _('%(time_left)s remaining') % \
                    {'time_left': project.module_running_time_left}
            else:
                return _('more than 1 year remaining')
        elif project.future_modules:
            return _('Participation: from %(project_start)s') % \
                {'project_start':
                    get_date_display(
                        project.future_modules.first().module_start)}
        elif project.past_modules:
            return _('Participation ended. Read result.')
        return ''

    def get_has_contact_info(self, project):
        if (project.contact_name or project.contact_address_text or
                project.contact_phone or project.contact_email or
                project.contact_url):
            return True
        return False


class AppPhaseSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Phase
        fields = ('name', 'description', 'type', 'start_date',
                  'end_date', 'is_active')

    def get_is_active(self, instance):
        if instance.start_date and instance.end_date:
            return instance.start_date <= timezone.now() <= instance.end_date
        return False


class AppModuleSerializer(serializers.ModelSerializer):
    phases = AppPhaseSerializer(many=True, read_only=True)
    labels = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    has_idea_adding_permission = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ('pk', 'phases', 'labels', 'categories',
                  'has_idea_adding_permission')

    def get_labels(self, instance):
        labels = Label.objects.filter(module=instance)
        if labels:
            return [{'id': label.pk, 'name': label.name} for label in labels]
        return False

    def get_categories(self, instance):
        categories = Category.objects.filter(module=instance)
        if categories:
            return [{'id': category.pk, 'name': category.name}
                    for category in categories]
        return False

    def get_has_idea_adding_permission(self, instance):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return user.has_perm('a4_candy_ideas.add_idea', instance)
        return False

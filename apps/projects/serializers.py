from functools import lru_cache

from django.utils.translation import ugettext as _
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from adhocracy4.projects.models import Project

from . import helpers


class ProjectSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    tile_image = serializers.SerializerMethodField()
    tile_image_copyright = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    participation_active = serializers.SerializerMethodField()
    participation_string = serializers.SerializerMethodField()
    future_phase = serializers.SerializerMethodField()
    active_phase = serializers.SerializerMethodField()
    past_phase = serializers.SerializerMethodField()
    offensive = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['title', 'url', 'organisation', 'tile_image',
                  'tile_image_copyright',
                  'status', 'access',
                  'participation_active',
                  'participation_string',
                  'future_phase', 'active_phase',
                  'past_phase',
                  'offensive', 'comment_count']

    @lru_cache(maxsize=1)
    def _get_participation_status_project(self, instance):
        project_phases = instance.phases

        if project_phases.active_phases():
            return _('running'), True

        if project_phases.future_phases():
            try:
                return (_('starts on {}').format
                        (project_phases.future_phases().first().
                         start_date.strftime('%d.%m.%y')),
                        True)
            except AttributeError:
                return (_('starts in the future'),
                        True)
        else:
            return _('completed'), False

    def get_type(self, instance):
        return 'project'

    def get_title(self, instance):
        return instance.name

    def get_url(self, instance):
        return instance.get_absolute_url()

    def get_organisation(self, instance):
        return instance.organisation.name

    def get_tile_image(self, instance):
        image_url = ''
        if instance.tile_image:
            image = get_thumbnailer(instance.tile_image)['project_thumbnail']
            image_url = image.url
        elif instance.image:
            image = get_thumbnailer(instance.image)['project_thumbnail']
            image_url = image.url
        return image_url

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
        participation_string, participation_active = \
            self._get_participation_status_project(instance)
        return participation_active

    def get_participation_string(self, instance):
        participation_string, participation_active = \
            self._get_participation_status_project(instance)
        return str(participation_string)

    def get_future_phase(self, instance):
        if (instance.future_modules and
                instance.future_modules.first().module_start):
            return str(
                instance.future_modules.first().module_start)
        return False

    def get_active_phase(self, instance):
        if instance.active_phase_ends_next:
            progress = instance.module_running_progress
            time_left = instance.module_running_time_left
            end_date = str(instance.running_module_ends_next.module_end)
            return [progress, time_left, end_date]
        return False

    def get_past_phase(self, instance):
        if (instance.past_modules and
                instance.past_modules.first().module_end):
            return str(
                instance.past_modules.first().module_end)
        return False

    def get_offensive(self, instance):
        return helpers.get_num_reported_comments(instance)

    def get_comment_count(self, instance):
        return helpers.get_num_comments_project(instance)

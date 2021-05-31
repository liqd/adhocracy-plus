from django.utils.html import strip_tags
from rest_framework import serializers

from adhocracy4.projects.models import Project


class AppProjectSerializer(serializers.ModelSerializer):

    information = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    # todo: remove many=True once AppProjects are restricted to single module
    published_modules = serializers.PrimaryKeyRelatedField(read_only=True,
                                                           many=True)
    access = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('pk', 'name', 'description', 'information', 'result',
                  'organisation', 'published_modules', 'access', 'image')

    def get_information(self, project):
        return strip_tags(project.information)

    def get_result(self, project):
        return strip_tags(project.result)

    def get_access(self, project):
        return project.access.name

from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from adhocracy4.projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    tile_image = serializers.SerializerMethodField()
    tile_image_copyright = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['title', 'url', 'organisation', 'tile_image',
                  'tile_image_copyright']

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

import rules

from apps.projects.models import Project


@rules.predicate
def is_moderator(user):
    return Project.objects.filter(moderators__id=user.id).exists()

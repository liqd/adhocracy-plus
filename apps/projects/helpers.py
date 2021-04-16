from django.db.models import Q

from adhocracy4.comments.models import Comment
from apps.classifications.models import AIClassification
from apps.classifications.models import UserClassification


def get_all_comments_project(project):

    return Comment.objects.filter(
        Q(budget_proposal__module__project=project) |
        Q(chapter__module__project=project) |
        Q(idea__module__project=project) |
        Q(mapidea__module__project=project) |
        Q(paragraph__chapter__module__project=project) |
        Q(poll__module__project=project) |
        Q(subject__module__project=project) |
        Q(topic__module__project=project) |
        # child comments
        Q(parent_comment__budget_proposal__module__project=project) |
        Q(parent_comment__chapter__module__project=project) |
        Q(parent_comment__idea__module__project=project) |
        Q(parent_comment__mapidea__module__project=project) |
        Q(parent_comment__paragraph__chapter__module__project=project) |
        Q(parent_comment__poll__module__project=project) |
        Q(parent_comment__subject__module__project=project) |
        Q(parent_comment__topic__module__project=project))


def get_num_comments_project(project):
    return get_all_comments_project(project).count()


def get_num_user_classifications(project):
    comments_project = get_all_comments_project(project)
    return UserClassification.objects.filter(
        comment__in=comments_project).count()


def get_num_ai_classifications(project):
    comments_project = get_all_comments_project(project)
    return AIClassification.objects.filter(
        comment__in=comments_project).count()


def get_num_classifications(project):
    return get_num_user_classifications(project) + \
        get_num_ai_classifications(project)

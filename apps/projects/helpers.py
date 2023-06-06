from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone

from adhocracy4.comments.models import Comment
from adhocracy4.reports.models import Report


def get_all_comments_project(project):
    return Comment.objects.filter(
        Q(project=project) | Q(parent_comment__project=project)
    )


def get_num_comments_project(project):
    return get_all_comments_project(project).count()


def get_num_reports(project):
    comment_ids_project = get_all_comments_project(project).values_list("id", flat=True)
    comment_ct = ContentType.objects.get_for_model(Comment)
    return Report.objects.filter(
        content_type=comment_ct, object_pk__in=comment_ids_project
    ).count()


def get_num_latest_comments(project, until={"days": 7}):
    all_comments_project = get_all_comments_project(project)
    return all_comments_project.filter(
        created__gte=timezone.now() - timedelta(**until)
    ).count()


def get_num_reported_unread_comments(project):
    unread_comments = get_all_comments_project(project).filter(is_reviewed=False)
    return (
        unread_comments.annotate(num_reports=Count("reports", distinct=True))
        .filter(num_reports__gt=0)
        .count()
    )

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from adhocracy4.comments.models import Comment
from adhocracy4.reports.models import Report


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


def get_reports_on_comments(project):
    comments_project = get_all_comments_project(project)
    comments_project_pks = comments_project.values_list('pk', flat=True)
    ct_comment = ContentType.objects.get(app_label='a4comments',
                                         model='comment')

    return Report.objects.filter(content_type=ct_comment).\
        filter(object_pk__in=comments_project_pks)


def get_reported_comments(project):
    comments_project = get_all_comments_project(project)
    ct_comment = ContentType.objects.get(app_label='a4comments',
                                         model='comment')
    reported_comments_pks = Report.objects.filter(content_type=ct_comment).\
        values_list('object_pk', flat=True)
    return comments_project.filter(pk__in=reported_comments_pks)


def get_num_reported_comments(project):
    return get_reported_comments(project).count()


def get_reported_comments_with_report(project):
    reports = get_reports_on_comments(project)
    return[(Comment.objects.get(pk=report.object_pk), report)
           for report in reports]

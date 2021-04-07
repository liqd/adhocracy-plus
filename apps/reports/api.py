from django.contrib.contenttypes.models import ContentType
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets

from adhocracy4.comments.models import Comment
from adhocracy4.reports import emails
from adhocracy4.reports.models import Report
from adhocracy4.reports.serializers import ReportSerializer
from apps.classifications.models import UserClassification

'''
overwrites ReportViewSet from adhocracy4 in order to
save a UserClassification object every time a comment is
reported
'''


class ReportViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = ReportSerializer
    queryset = Report.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        report = serializer.save(creator=self.request.user)
        emails.ReportModeratorEmail.send(report)
        if serializer.data['content_type'] == \
            ContentType.objects.get(app_label='a4comments',
                                    model='comment').pk:

            classification = UserClassification(
                creator=self.request.user,
                comment=Comment.objects.get(pk=serializer.data['object_pk']),
                classification='OFFENSIVE',
                user_message=serializer.data['description'])
            classification.save()

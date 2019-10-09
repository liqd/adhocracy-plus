from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from adhocracy4.api.mixins import ModuleMixin
from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(ModuleMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet,
                      ):

    serializer_class = QuestionSerializer
    permission_classes = (ViewSetRulesPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('is_answered', 'is_live', 'is_hidden')
    ordering_fields = ('like_count',)

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        questions = Question\
            .objects\
            .filter(module=self.module)\
            .order_by('created')\
            .annotate_like_count()
        if not self.request.user.has_perm(
            'a4_candy_questions.moderate_questions', self.module
        ):
            questions = questions.filter(is_hidden=False)
        return questions

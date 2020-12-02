import json

from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from adhocracy4.api.mixins import ModuleMixin
from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import Like
from .models import LiveQuestion
from .serializers import LikeSerializer
from .serializers import LiveQuestionSerializer


class LiveQuestionViewSet(ModuleMixin,
                          mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet,
                          ):

    serializer_class = LiveQuestionSerializer
    permission_classes = (ViewSetRulesPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_fields = ('is_answered', 'is_live', 'is_hidden')
    ordering_fields = ('like_count',)

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        live_questions = LiveQuestion\
            .objects\
            .filter(module=self.module)\
            .order_by('created')\
            .annotate_like_count()
        if not self.request.user.has_perm(
            'a4_candy_livequestions.moderate_livequestions', self.module
        ):
            live_questions = live_questions.filter(is_hidden=False)
        return live_questions

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            body = json.loads(request.body.decode("utf-8"))
            kwargs['category'] = body['category']
        return super().dispatch(request, *args, **kwargs)


class LikesViewSet(mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = LikeSerializer
    permission_classes = (ViewSetRulesPermission,)

    def dispatch(self, request, *args, **kwargs):
        self.livequestion_pk = kwargs.get('livequestion_pk', '')
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.livequestion

    def get_queryset(self):
        return Like.objects.filter(livequestion=self.livequestion)

    def perform_create(self, serializer):
        if not self.request.session.session_key:
            self.request.session.create()
        session = Session.objects.get(
            session_key=self.request.session.session_key)
        like_value = bool(self.request.data['value'])
        if like_value:
            serializer.save(session=session, livequestion=self.livequestion)
        elif Like.objects.filter(session=session,
                                 livequestion=self.livequestion).exists():
            Like.objects.get(session=session,
                             livequestion=self.livequestion).delete()

    @property
    def livequestion(self):
        return get_object_or_404(
            LiveQuestion,
            pk=self.livequestion_pk
        )

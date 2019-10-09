from django.db import models

from apps.questions.models import Question


class Like(models.Model):
    session = models.CharField(max_length=255)
    question = models.ForeignKey(Question,
                                 related_name='question_likes',
                                 on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'question')

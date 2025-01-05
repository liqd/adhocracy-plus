from django.db.models import signals
from django.dispatch import receiver

from adhocracy4.comments.models import Comment
from adhocracy4.polls.models import Answer
from adhocracy4.polls.models import Vote
from adhocracy4.polls.signals import poll_voted
from adhocracy4.projects.models import Project
from adhocracy4.ratings.models import Rating
from apps.budgeting.models import Proposal
from apps.ideas.models import Idea
from apps.interactiveevents.models import Like
from apps.interactiveevents.models import LiveQuestion
from apps.mapideas.models import MapIdea
from apps.topicprio.models import Topic

from . import emails
from .models import ProjectInsight


@receiver(signals.m2m_changed, sender=Project.participants.through)
def send_welcome_to_private_project_email(action, **kwargs):
    if action == "post_add":
        project = kwargs.get("instance")
        participant_pks = list(kwargs.get("pk_set"))

        emails.WelcomeToPrivateProjectEmail.send(
            project, participant_pks=participant_pks
        )


@receiver(signals.post_save, sender=Comment)
def increase_comments_count(sender, instance, created, **kwargs):
    if created and instance.project:
        insight, _ = ProjectInsight.objects.get_or_create(project=instance.project)
        insight.comments += 1
        insight.save()
        insight.active_participants.add(instance.creator.id)


@receiver(signals.post_save, sender=Idea)
@receiver(signals.post_save, sender=MapIdea)
@receiver(signals.post_save, sender=Proposal)
@receiver(signals.post_save, sender=Topic)
def increase_idea_count(sender, instance, created, **kwargs):
    if not created:
        return

    insight, _ = ProjectInsight.objects.get_or_create(project=instance.module.project)
    insight.written_ideas += 1
    insight.save()

    if sender != Topic:
        insight.active_participants.add(instance.creator.id)


@receiver(signals.post_save, sender=Rating)
def increase_rating_count(sender, instance, created, **kwargs):
    if created:
        insight, _ = ProjectInsight.objects.get_or_create(
            project=instance.module.project
        )
        insight.ratings += 1
        insight.active_participants.add(instance.creator.id)
        insight.save()


@receiver(signals.post_save, sender=LiveQuestion)
def increase_live_questions_count(sender, instance, created, **kwargs):
    if created:
        project = instance.module.project
        insight, _ = ProjectInsight.objects.get_or_create(project=project)
        insight.live_questions += 1
        insight.save()


@receiver(signals.post_save, sender=Like)
def increase_ratings_count_for_likes(sender, instance, created, **kwargs):
    if created:
        project = instance.livequestion.module.project
        insight, _ = ProjectInsight.objects.get_or_create(project=project)
        insight.ratings += 1
        insight.save()


@receiver(signals.post_save, sender=Vote)
@receiver(signals.post_save, sender=Answer)
def increase_poll_answers_count(sender, instance, created, **kwargs):
    if created:
        if sender == Answer:
            project = instance.question.poll.module.project
        else:
            project = instance.project

        insight, _ = ProjectInsight.objects.get_or_create(project=project)
        insight.poll_answers += 1
        insight.save()


@receiver(poll_voted)
def increase_poll_participant_count(sender, poll, creator, content_id, **kwargs):
    insight, _ = ProjectInsight.objects.get_or_create(project=poll.module.project)
    if creator:
        insight.active_participants.add(creator.id)
    else:
        insight.unregistered_participants += 1
    insight.save()

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
from .insights import remove_active_participant_if_inactive
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


# post_delete handlers mirror the post_save increment handlers above: each
# decrements the matching ProjectInsight counter. Where the corresponding
# post_save handler also adds the creator to active_participants, the delete
# handler calls remove_active_participant_if_inactive so the user is only
# removed when they have no remaining contributions in the project.


@receiver(signals.post_delete, sender=Comment)
def decrease_comments_count(sender, instance, **kwargs):
    if not instance.project_id:
        return

    project = instance.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.comments = max(0, insight.comments - 1)
    insight.save()
    remove_active_participant_if_inactive(
        insight=insight, project=project, user_id=instance.creator_id
    )


@receiver(signals.post_delete, sender=Idea)
@receiver(signals.post_delete, sender=MapIdea)
@receiver(signals.post_delete, sender=Proposal)
@receiver(signals.post_delete, sender=Topic)
def decrease_idea_count(sender, instance, **kwargs):
    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.written_ideas = max(0, insight.written_ideas - 1)
    insight.save()

    if sender != Topic:
        remove_active_participant_if_inactive(
            insight=insight, project=project, user_id=instance.creator_id
        )


@receiver(signals.post_delete, sender=Rating)
def decrease_rating_count(sender, instance, **kwargs):
    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.ratings = max(0, insight.ratings - 1)
    insight.save()
    remove_active_participant_if_inactive(
        insight=insight, project=project, user_id=instance.creator_id
    )


@receiver(signals.post_delete, sender=LiveQuestion)
def decrease_live_questions_count(sender, instance, **kwargs):
    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.live_questions = max(0, insight.live_questions - 1)
    insight.save()


@receiver(signals.post_delete, sender=Like)
def decrease_ratings_count_for_likes(sender, instance, **kwargs):
    project = instance.livequestion.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.ratings = max(0, insight.ratings - 1)
    insight.save()


@receiver(signals.post_delete, sender=Vote)
@receiver(signals.post_delete, sender=Answer)
def decrease_poll_answers_count(sender, instance, **kwargs):
    if sender == Answer:
        project = instance.question.poll.module.project
    else:
        project = instance.project

    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.poll_answers = max(0, insight.poll_answers - 1)
    insight.save()
    remove_active_participant_if_inactive(
        insight=insight, project=project, user_id=instance.creator_id
    )

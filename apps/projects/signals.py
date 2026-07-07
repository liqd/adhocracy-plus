from django.db.models import signals
from django.dispatch import receiver

from adhocracy4.comments.models import Comment
from adhocracy4.modules.models import Module
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
from .insights import add_active_participant
from .insights import comment_counts_toward_insights
from .insights import create_insight
from .insights import get_insight_module
from .insights import module_counts_toward_insights
from .insights import rating_counts_toward_insights
from .insights import remove_active_participant_if_inactive
from .insights import sync_unregistered_participants
from .models import ProjectInsight


def _insight_module_for_instance(instance):
    if isinstance(instance, Comment):
        return get_insight_module(instance.content_object)
    if isinstance(instance, Like):
        return instance.livequestion.module
    if isinstance(instance, Vote):
        return instance.choice.question.poll.module
    if isinstance(instance, Answer):
        return instance.question.poll.module
    if isinstance(instance, Rating):
        return instance.module
    return get_insight_module(instance)


@receiver(signals.m2m_changed, sender=Project.participants.through)
def send_welcome_to_private_project_email(action, **kwargs):
    if action == "post_add":
        project = kwargs.get("instance")
        participant_pks = list(kwargs.get("pk_set"))

        emails.WelcomeToPrivateProjectEmail.send(
            project, participant_pks=participant_pks
        )


@receiver(signals.pre_save, sender=Module)
def cache_module_is_draft(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_is_draft = (
            Module.objects.filter(pk=instance.pk)
            .values_list("is_draft", flat=True)
            .first()
        )
    else:
        instance._previous_is_draft = None


@receiver(signals.post_save, sender=Module)
def refresh_insights_on_module_draft_change(sender, instance, **kwargs):
    previous_is_draft = getattr(instance, "_previous_is_draft", None)
    if previous_is_draft is not None and previous_is_draft != instance.is_draft:
        create_insight(project=instance.project)


@receiver(signals.pre_save, sender=Comment)
# Comment deletes are soft (is_removed etc.); see update_comments_count and
# comment_counts_toward_insights in insights.py.
def cache_comment_counted_state(sender, instance, **kwargs):
    if instance.pk:
        previous = Comment.objects.get(pk=instance.pk)
        instance._was_counted_toward_insights = comment_counts_toward_insights(previous)
    else:
        instance._was_counted_toward_insights = False


@receiver(signals.post_save, sender=Comment)
def update_comments_count(sender, instance, created, **kwargs):
    if not instance.project_id:
        return

    was_counted = getattr(instance, "_was_counted_toward_insights", False)
    is_counted = comment_counts_toward_insights(instance)

    if was_counted == is_counted:
        return

    project = instance.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)

    if is_counted:
        insight.comments += 1
        insight.save()
        add_active_participant(insight, instance.creator_id)
    else:
        insight.comments = max(0, insight.comments - 1)
        insight.save()
        remove_active_participant_if_inactive(
            insight=insight, project=project, user_id=instance.creator_id
        )


@receiver(signals.post_save, sender=Idea)
@receiver(signals.post_save, sender=MapIdea)
@receiver(signals.post_save, sender=Proposal)
@receiver(signals.post_save, sender=Topic)
def increase_idea_count(sender, instance, created, **kwargs):
    if not created:
        return
    if not module_counts_toward_insights(instance.module):
        return

    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.written_ideas += 1
    insight.save()

    if sender != Topic:
        add_active_participant(insight, instance.creator_id)


@receiver(signals.pre_save, sender=Rating)
def cache_rating_value(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_rating_value = (
            Rating.objects.filter(pk=instance.pk)
            .values_list("value", flat=True)
            .first()
        )
    else:
        instance._previous_rating_value = None


@receiver(signals.post_save, sender=Rating)
def update_rating_count(sender, instance, created, **kwargs):
    module = instance.module
    if not module_counts_toward_insights(module):
        return

    previous_value = getattr(instance, "_previous_rating_value", None)
    previous_counts = rating_counts_toward_insights(previous_value)
    current_counts = rating_counts_toward_insights(instance.value)

    if created:
        if not current_counts:
            return
        delta = 1
    elif previous_counts == current_counts:
        return
    else:
        delta = 1 if current_counts else -1

    project = module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.ratings = max(0, insight.ratings + delta)
    insight.save()

    if current_counts:
        add_active_participant(insight, instance.creator_id)
    elif previous_counts:
        remove_active_participant_if_inactive(
            insight=insight, project=project, user_id=instance.creator_id
        )


@receiver(signals.post_save, sender=LiveQuestion)
def increase_live_questions_count(sender, instance, created, **kwargs):
    if not created:
        return
    if not module_counts_toward_insights(instance.module):
        return

    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.live_questions += 1
    insight.save()


@receiver(signals.post_save, sender=Like)
def increase_ratings_count_for_likes(sender, instance, created, **kwargs):
    if not created:
        return
    module = instance.livequestion.module
    if not module_counts_toward_insights(module):
        return

    project = module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.ratings += 1
    insight.save()


@receiver(signals.post_save, sender=Vote)
@receiver(signals.post_save, sender=Answer)
def increase_poll_answers_count(sender, instance, created, **kwargs):
    if not created:
        return

    module = _insight_module_for_instance(instance)
    if not module_counts_toward_insights(module):
        return

    project = module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.poll_answers += 1
    insight.save()
    add_active_participant(insight, instance.creator_id)


@receiver(poll_voted)
def increase_poll_participant_count(sender, poll, creator, content_id, **kwargs):
    if not module_counts_toward_insights(poll.module):
        return

    project = poll.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    if creator:
        add_active_participant(insight, creator.id)
    else:
        sync_unregistered_participants(insight=insight, project=project)


# post_delete handlers mirror the post_save increment handlers above: each
# decrements the matching ProjectInsight counter. Where the corresponding
# post_save handler also adds the creator to active_participants, the delete
# handler calls remove_active_participant_if_inactive so the user is only
# removed when they have no remaining contributions in the project.


@receiver(signals.post_delete, sender=Comment)
def decrease_comments_count(sender, instance, **kwargs):
    if not instance.project_id:
        return
    if not comment_counts_toward_insights(instance):
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
    if not module_counts_toward_insights(instance.module):
        return

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
    if not rating_counts_toward_insights(instance.value):
        return
    if not module_counts_toward_insights(instance.module):
        return

    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.ratings = max(0, insight.ratings - 1)
    insight.save()
    remove_active_participant_if_inactive(
        insight=insight, project=project, user_id=instance.creator_id
    )


@receiver(signals.post_delete, sender=LiveQuestion)
def decrease_live_questions_count(sender, instance, **kwargs):
    if not module_counts_toward_insights(instance.module):
        return

    project = instance.module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.live_questions = max(0, insight.live_questions - 1)
    insight.save()


@receiver(signals.post_delete, sender=Like)
def decrease_ratings_count_for_likes(sender, instance, **kwargs):
    module = instance.livequestion.module
    if not module_counts_toward_insights(module):
        return

    project = module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.ratings = max(0, insight.ratings - 1)
    insight.save()


@receiver(signals.post_delete, sender=Vote)
@receiver(signals.post_delete, sender=Answer)
def decrease_poll_answers_count(sender, instance, **kwargs):
    module = _insight_module_for_instance(instance)
    if not module_counts_toward_insights(module):
        return

    project = module.project
    insight, _ = ProjectInsight.objects.get_or_create(project=project)
    insight.poll_answers = max(0, insight.poll_answers - 1)
    insight.save()

    if instance.creator_id:
        remove_active_participant_if_inactive(
            insight=insight, project=project, user_id=instance.creator_id
        )
    else:
        sync_unregistered_participants(insight=insight, project=project)

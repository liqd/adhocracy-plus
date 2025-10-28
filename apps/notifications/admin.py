from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import path

from apps.notifications import strategies
from apps.notifications.models import NotificationType
from apps.notifications.services import NotificationService
from apps.projects.models import Project

User = get_user_model()


@staff_member_required
def notification_strategies_overview(request):
    strategies_data = []

    for notification_type in NotificationType:
        email_class = NotificationService._map_notification_type_to_email_class(
            notification_type
        )
        strategy_class = _get_strategy_for_type(notification_type)

        if email_class and strategy_class:
            template_name = getattr(email_class, "template_name", None)

            try:
                rendered = _render_email_template(
                    email_class, strategy_class, template_name, request.user
                )
            except Exception as e:
                rendered = f"Error: {str(e)}"

            strategies_data.append(
                {
                    "notification_type": notification_type.label,
                    "email_class": email_class.__name__,
                    "strategy_class": strategy_class.__name__,
                    "template_name": template_name,
                    "rendered": rendered,
                }
            )

    return render(
        request,
        "admin/notification_strategies_overview.html",
        {
            "title": "Email Templates",
            "strategies": strategies_data,
        },
    )


def _get_strategy_for_type(notification_type):
    """Map notification type to strategy class"""
    strategy_map = {
        NotificationType.MODERATOR_COMMENT_FEEDBACK: strategies.CommentFeedback,
        NotificationType.MODERATOR_IDEA_FEEDBACK: strategies.IdeaFeedback,
        NotificationType.MODERATOR_BLOCKED_COMMENT: strategies.CommentBlocked,
        NotificationType.PROJECT_STARTED: getattr(strategies, "ProjectStarted", None),
        NotificationType.PROJECT_COMPLETED: getattr(strategies, "ProjectEnded", None),
        NotificationType.COMMENT_REPLY: getattr(strategies, "CommentReply", None),
        NotificationType.COMMENT_ON_POST: getattr(strategies, "ProjectComment", None),
        NotificationType.PROJECT_CREATED: getattr(strategies, "ProjectCreated", None),
        NotificationType.PROJECT_DELETED: getattr(strategies, "ProjectDeleted", None),
        NotificationType.EVENT_SOON: getattr(strategies, "OfflineEventReminder", None),
        NotificationType.EVENT_ADDED: getattr(strategies, "OfflineEventCreated", None),
        NotificationType.USER_CONTENT_CREATED: getattr(
            strategies, "UserContentCreated", None
        ),
    }
    return strategy_map.get(notification_type)


def _render_email_template(email_class, strategy_class, template_name, current_user):
    """Render the email template using real data"""
    try:
        from django.template.loader import get_template

        template_path = f"{template_name}.en.email"
        template = get_template(template_path)

        # Get real project from database
        real_project = Project.objects.first()
        if not real_project:
            return "No projects found in database"

        # Create strategy instance with real data
        strategy_instance = strategy_class()
        mock_object = _create_mock_object(
            strategy_class.__name__, real_project, current_user
        )
        notification_data = strategy_instance.create_notification_data(mock_object)
        strategy_context = notification_data.get("context", {})

        # Create email instance
        email_instance = email_class()
        email_instance.object = mock_object
        email_instance.kwargs = {}

        # Get email context if available
        email_context = (
            email_instance.get_context()
            if hasattr(email_instance, "get_context")
            else {}
        )

        # Merge contexts
        context = {**strategy_context, **email_context}
        context.update(
            {
                "email": email_instance,
                "site": (
                    email_instance.get_site()
                    if hasattr(email_instance, "get_site")
                    else type(
                        "MockSite", (), {"name": "Test Site", "domain": "example.com"}
                    )()
                ),
                "receiver": current_user,  # Use the logged-in admin as recipient
                "part_type": "html",
            }
        )

        return template.render(context)

    except Exception as e:
        return f"Error rendering: {str(e)}"


def _create_mock_object(strategy_class_name, real_project, current_user):
    """Create mock object using real data from database"""
    if "Comment" in strategy_class_name:
        # Use real Comment if available
        from adhocracy4.comments.models import Comment

        real_comment = Comment.objects.filter(project=real_project).first()
        if real_comment:
            return real_comment
        else:
            return type(
                "MockComment",
                (),
                {
                    "comment": "This is a test comment for email preview",
                    "creator": current_user,
                    "project": real_project,
                    "get_absolute_url": lambda: "/comments/1",
                },
            )()

    elif "Idea" in strategy_class_name:
        # Use real Idea if available
        from apps.ideas.models import Idea

        real_idea = Idea.objects.filter(project=real_project).first()
        if real_idea:
            return real_idea
        else:
            return type(
                "MockIdea",
                (),
                {
                    "name": "Test Idea for Email Preview",
                    "creator": current_user,
                    "project": real_project,
                    "get_absolute_url": lambda: "/ideas/1",
                },
            )()

    elif "Proposal" in strategy_class_name:
        # Use real Proposal if available
        from apps.budgeting.models import Proposal

        real_proposal = Proposal.objects.filter(project=real_project).first()
        if real_proposal:
            return real_proposal
        else:
            return type(
                "MockProposal",
                (),
                {
                    "name": "Test Proposal for Email Preview",
                    "creator": current_user,
                    "project": real_project,
                    "get_absolute_url": lambda: "/proposals/1",
                },
            )()

    elif "Project" in strategy_class_name:
        return real_project

    elif "Event" in strategy_class_name:
        # Use real OfflineEvent if available
        from apps.offlineevents.models import OfflineEvent

        real_event = OfflineEvent.objects.filter(project=real_project).first()
        if real_event:
            return real_event
        else:
            return type(
                "MockEvent",
                (),
                {
                    "name": "Test Event for Email Preview",
                    "project": real_project,
                    "date": "2024-01-01 14:00:00",
                    "get_absolute_url": lambda: "/events/1",
                },
            )()

    else:
        return type(
            "MockObject",
            (),
            {
                "name": "Test Object for Email Preview",
                "project": real_project,
                "get_absolute_url": lambda: "/objects/1",
            },
        )()


def get_admin_urls():
    return [path("notification-strategies/", notification_strategies_overview)]


original_get_urls = admin.site.get_urls
admin.site.get_urls = lambda: get_admin_urls() + original_get_urls()

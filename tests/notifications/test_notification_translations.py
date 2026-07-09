import pytest
from django.utils import translation

from apps.notifications.models import Notification
from apps.notifications.models import NotificationType
from apps.notifications.templatetags.notification_tags import (
    render_notification_with_links,
)

from .factories import NotificationFactory


@pytest.mark.django_db
class TestContextValueTranslation:
    """Verify that notification context values are stored as raw English keys
    and translated at render time (bugs #3 and #4)."""

    def test_non_link_value_passes_through_gettext_at_render_time(self):
        """Non-link context values should go through _() at render time."""
        notification = NotificationFactory(
            message_template="New {content_type} created",
            context={"content_type": "idea"},
            notification_type=NotificationType.USER_CONTENT_CREATED,
        )
        with translation.override("en"):
            result = render_notification_with_links(notification)
        # "idea" is the English msgid — it renders unchanged in English
        assert "New idea created" in result

    def test_link_value_passes_through_gettext_at_render_time(self):
        """Link-bearing context values should already go through _() at render time."""
        notification = NotificationFactory(
            message_template="Feedback on your {comment}",
            context={
                "comment": "comment",
                "comment_url": "http://example.com/comment/1/",
            },
            notification_type=NotificationType.MODERATOR_COMMENT_FEEDBACK,
        )
        with translation.override("en"):
            result = render_notification_with_links(notification)
        # Verify it renders a clickable link with "comment" as the link text
        assert "Feedback on your" in result
        assert "mark-as-read" in result
        assert "comment" in result
        assert "redirect_to=http://example.com/comment/1/" in result

    def test_non_link_value_does_not_crash_on_data_strings(self):
        """Data values (project names, usernames) pass through _() harmlessly."""
        notification = NotificationFactory(
            message_template="Project {project} is ready",
            context={"project": "My Park Project"},
            notification_type=NotificationType.PROJECT_STARTED,
        )
        with translation.override("en"):
            result = render_notification_with_links(notification)
        # "My Park Project" is not a msgid, so _() returns it unchanged
        assert "Project My Park Project is ready" in result

    def test_replied_value_is_link_translated_at_render_time(self):
        """{replied} has replied_url so it goes through the link path which calls _()"""
        notification = NotificationFactory(
            message_template="{user} {replied} to your comment",
            context={
                "user": "John",
                "replied": "replied",
                "replied_url": "http://example.com/comment/1/",
                "project": "Test Project",
                "project_url": "http://example.com/project/1/",
            },
            notification_type=NotificationType.COMMENT_REPLY,
        )
        with translation.override("en"):
            result = render_notification_with_links(notification)
        # With English locale, "replied" passes through _() unchanged (no translation)
        # The link wraps "replied" in <a> tag
        assert "John" in result
        assert "replied" in result
        assert "mark-as-read" in result


@pytest.mark.django_db
class TestContextStorageUnderNonEnglishLanguage:
    """Verify that context values are stored as raw English keys regardless
    of the language active at notification creation time."""

    def test_user_content_created_stores_raw_content_type(self):
        """UserContentCreated should store 'idea' not 'Idee' even when
        created under German language."""
        with translation.override("de"):
            notification = NotificationFactory(
                message_template='A new {content_type} "{content}" has been created',
                context={
                    "content_type": "idea",
                    "content_type_display": "idea",
                    "content": "My Idea",
                },
                notification_type=NotificationType.USER_CONTENT_CREATED,
            )
        assert (
            notification.context["content_type"] == "idea"
        ), "Should store raw English key, not German 'Idee'"
        assert (
            notification.context["content_type_display"] == "idea"
        ), "Should store raw English key"

    def test_comment_feedback_stores_raw_comment(self):
        """CommentFeedback should store 'comment' not 'Kommentar' when
        created under German language."""
        with translation.override("de"):
            notification = NotificationFactory(
                message_template="A moderator gave feedback on your {comment}",
                context={
                    "comment": "comment",
                    "comment_url": "http://example.com/comment/1/",
                },
                notification_type=NotificationType.MODERATOR_COMMENT_FEEDBACK,
            )
        assert (
            notification.context["comment"] == "comment"
        ), "Should store raw English 'comment', not German 'Kommentar'"


@pytest.mark.django_db
class TestIntegrationSignalTriggers:
    """Full integration tests — trigger actual signals and verify context values."""

    def test_idea_created_signal_stores_raw_content_type_under_german(
        self, project_factory, module_factory, user_factory, idea_factory
    ):
        """When an idea is created while German is active, the resulting
        UserContentCreated notification stores raw 'idea' not 'Idee'."""
        project = project_factory()
        module = module_factory(project=project)
        idea_author = user_factory()

        with translation.override("de"):
            idea = idea_factory(module=module, creator=idea_author)

        moderator = idea.project.moderators.first()
        notifications = Notification.objects.filter(
            recipient=moderator,
            notification_type=NotificationType.USER_CONTENT_CREATED,
        )
        assert notifications.count() == 1
        notification = notifications.first()

        assert (
            notification.context["content_type"] == "idea"
        ), "content_type should be raw 'idea', not frozen German 'Idee'"
        assert (
            notification.context["content_type_display"] == "idea"
        ), "content_type_display should be raw 'idea'"

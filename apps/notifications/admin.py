from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import os
from django.conf import settings

from apps.notifications import strategies
from apps.notifications.models import NotificationType
from apps.notifications.services import NotificationService
from apps.projects.models import Project

User = get_user_model()


@staff_member_required
def notification_strategies_overview(request):
    if request.method == 'POST':
        return _handle_template_save(request)
    
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
                template_content = _get_template_source(template_name)
                template_path = _get_template_path(template_name)
                context_variables = _get_context_variables(strategy_class, request.user)
            except Exception as e:
                rendered = f"Error: {str(e)}"
                template_content = f"Error: {str(e)}"
                template_path = None
                context_variables = []

            strategies_data.append(
                {
                    'notification_type': notification_type.label,
                    'email_class': email_class.__name__,
                    'strategy_class': strategy_class.__name__,
                    'template_name': template_name,
                    'rendered': rendered,
                    'template_content': template_content,
                    'template_path': template_path,
                    'context_variables': context_variables,
                }
            )

    return render(
        request,
        'admin/notification_strategies_overview.html',
        {
            'title': 'Email Templates',
            'strategies': strategies_data,
        },
    )

def _get_context_variables(strategy_class, current_user):
    """Get available context variables from the strategy"""
    try:
        # Create strategy instance
        strategy_instance = strategy_class()
        
        # Get real project from database for mock data
        real_project = Project.objects.first()
        if not real_project:
            return ["No projects found - cannot generate context variables"]
        
        # Create mock object
        mock_object = _create_mock_object(
            strategy_class.__name__, real_project, current_user
        )
        
        # Get notification data
        notification_data = strategy_instance.create_notification_data(mock_object)
        context = notification_data.get("context", {})
        
        # Format context variables for display
        context_vars = []
        for key, value in context.items():
            var_type = type(value).__name__
            var_preview = str(value)
            if len(var_preview) > 50:
                var_preview = var_preview[:50] + "..."
            context_vars.append({
                'name': key,
                'type': var_type,
                'preview': var_preview
            })
        
        return context_vars
        
    except Exception as e:
        return [f"Error getting context: {str(e)}"]
        
def _handle_template_save(request):
    """Handle template saving with Django messages"""
    template_name = request.POST.get('template_name')
    content = request.POST.get('content')
    
    if not template_name or content is None:
        messages.error(request, 'Missing template name or content')
        return redirect('notification_strategies')
    
    try:
        template_path = _get_template_path(template_name)
        
        if not template_path:
            messages.error(request, f'Could not determine path for template: {template_name}')
            return redirect('notification_strategies')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        # Write the content to file
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        messages.success(request, f'Template {template_name} saved successfully!')
        
    except Exception as e:
        messages.error(request, f'Error saving template: {str(e)}')
    
    return redirect('notification_strategies')


def _get_template_path(template_name):
    """Get the full filesystem path for a template"""
    if not template_name:
        return None
    
    # The template_name already includes the full path, just add the extension
    template_filename = f"{template_name}.en.email"
    
    # Look for template in template directories
    for template_dir in settings.TEMPLATES[0]['DIRS']:
        template_path = os.path.join(template_dir, template_filename)
        if os.path.exists(template_path):
            return template_path
    
    # If not found in template dirs, check in app templates
    for app in settings.INSTALLED_APPS:
        try:
            app_module = __import__(app)
            app_path = app_module.__path__[0]
            # Look for template in app's templates directory
            template_path = os.path.join(app_path, 'notifications/templates', template_filename)
            if os.path.exists(template_path):
                return template_path
        except (ImportError, AttributeError, IndexError):
            continue
    
    # If template doesn't exist anywhere, return the path where it should be created
    # Look in all installed apps for the most appropriate location
    for app in settings.INSTALLED_APPS:
        if 'notifications' in app:
            try:
                app_module = __import__(app)
                app_path = app_module.__path__[0]
                return os.path.join(app_path, 'templates', template_filename)
            except (ImportError, AttributeError, IndexError):
                continue
    
    # Fallback: use the first template directory
    if settings.TEMPLATES[0]['DIRS']:
        return os.path.join(settings.TEMPLATES[0]['DIRS'][0], template_filename)
    else:
        # Final fallback to base directory templates
        return os.path.join(settings.BASE_DIR, 'templates', template_filename)


def _get_template_source(template_name):
    """Get the template source code"""
    if not template_name:
        return "No template name available"
    
    template_path = _get_template_path(template_name)
    
    if not template_path:
        return f"# Could not find template path for: {template_name}"
    
    try:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"# Template file not found at: {template_path}\n# This template will be created when you save it\n\n# Add your template content here"
    except Exception as e:
        return f"# Error reading template: {str(e)}"


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

        if not template_name:
            return "No template name available"

        template_path = f"{template_name}.en.email"
        
        # Check if template exists before trying to render
        if not _get_template_path(template_name):
            return f"Template not found: {template_path}"

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
                "receiver": current_user,
                "part_type": "html",
            }
        )

        return template.render(context)

    except Exception as e:
        return f"Error rendering template: {str(e)}"


def _create_mock_object(strategy_class_name, real_project, current_user):
    """Create mock object using real data from database"""
    if "Comment" in strategy_class_name:
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


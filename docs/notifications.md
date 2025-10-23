# Notifications System Documentation

Important file: `apps/notifications/helpers.py`

### Models

- contained in  `apps/notifications/models`
- Notification Model with attributes such as:
    - message_template
    - notification_type
    - recipient
- NotificationChannel (in-app vs email)
- NotificationCategory
- NotificationSettings model - user preferences for which notifications they should receive

### Strategy Pattern Implementation

The system uses a strategy pattern to handle different notification types.

A strategy contains the following functions

- `get_in_app_recipients`
- `get_email_recipients`
- `create_notification__data`

The BaseNotification class is found at `apps/notifications/strategies/base.py`

`apps/notifications/strategies` contains files for each category of strategies, for example `comment_strategies`

#### Example notification data:
```
def create_notification_data(self, offline_event):
    """Create notification data for offline events"""
    return {
        'notification_type': NotificationType.EVENT_ADDED,
        'title': _("New event in {}").format(offline_event.project.name),
        'message_template': _("A new event '{event}' has been added to the project {project}"),
        'context': {
            'project': offline_event.project.name,
            'project_url': offline_event.project.get_absolute_url(),
            'event': offline_event.name,
            'event_url': offline_event.get_absolute_url(),
        }
    }
```


### Signals 

`apps/notifications/signals.py` contains signals which catch various pre_save and post_save signals, and creates relevant notifications.

### Celery Tasks

Tasks (in `notifications/tasks.py`) are run via celery once per day to check for phases / projects / events which have started / ended or will be starting within 24 hours.

- `send_recently_started_phase_notifications`
- `send_recently_completed_phase_notifications`
- `send_upcoming_event_notifications`

### Views

NotificationsDashboardView defines the notifications overview page, and  creates two lists of notifications 

```
context["interactions_page"] = self._paginate_queryset(
            interactions, page_param="interactions_page"
)
context["projects_page"] = self._paginate_queryset(
    followed_projects, page_param="projects_page"
)
```

which are rendered using the templates:

`apps/notifications/templates/a4_candy_notifications/_notification_card.html`
`apps/notifications/templates/a4_candy_notifications/_notification_list.html`

and each individual notification is loaded via filter `render_notification_with_links()` (`apps/notifications/templatetags/notification_tags.py`)
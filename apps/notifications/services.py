# In your service layer
from .factories import NotificationStrategyFactory
from . import emails
class NotificationService:
    def __init__(self):
        self.strategy_factory = NotificationStrategyFactory()
    
    def handle_action(self, action):
        strategy = self.strategy_factory.get_strategy(action)
        if not strategy:
            return 0
        
        # Get recipients
        in_app_recipients = strategy.get_in_app_recipients(action)
        email_recipients = strategy.get_email_recipients(action)
        
        # Create notifications
        notifications = []
        for recipient in in_app_recipients:
            notification_data = strategy.create_notification_data(action, recipient)
            notifications.append(Notification(
                recipient=recipient,
                notification_type=action.type,
                **notification_data
            ))
        
        if notifications:
            Notification.objects.bulk_create(notifications)
        
        # Send emails
        for recipient in email_recipients:
            self.send_email(recipient, action, strategy)
        
        return len(notifications)

    def send_email(self, recipient, action, strategy):
        """Use existing email system instead of rebuilding"""
        email_class = self._map_action_to_email_class(action)
        if email_class:
            email_class.send(action)
            
    def _map_action_to_email_class(self, action):
        email_map = {
            NotificationType.USER_ENGAGEMENT: emails.NotifyCreatorEmail,
            NotificationType.PROJECT_UPDATE: emails.NotifyFollowersOnPhaseStartedEmail,
            NotificationType.PROJECT_EVENT: emails.NotifyFollowersOnUpcommingEventEmail,
            NotificationType.MODERATOR_FEEDBACK: emails.NotifyCreatorOnModeratorCommentFeedback,
        }
        return email_map.get(action.notification_type)
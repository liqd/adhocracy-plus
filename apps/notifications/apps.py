from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    
    def ready(self):
        # Import and initialize services
        from .services import NotificationService
        from .strategies import (
            UserEngagementStrategy, 
            ProjectUpdatesStrategy,
            ProjectEventsStrategy
        )
        
        self.notification_service = NotificationService()
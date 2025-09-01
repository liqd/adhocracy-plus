class CommentNotificationStrategy:
    """Handle comment-related notifications"""
    
    def can_handle(self, action):
        return (action.obj_content_type == ContentType.objects.get_for_model(Comment) and 
                action.verb == "add")
    
    def handle(self, action, notification_service):
        # Exclude actions on polls and documents
        excluded_ct = [
            ContentType.objects.get_for_model(Poll),
            ContentType.objects.get_for_model(Chapter),
            ContentType.objects.get_for_model(Paragraph),
        ]
        
        if action.target_content_type in excluded_ct:
            return False
        
        # Skip if comment is blocked or user is commenting on their own content
        if (hasattr(action.obj, 'is_blocked') and action.obj.is_blocked) or action.actor == action.target_creator:
            return False
        
        # Create notification
        notification_service.create_notification(
            recipient=action.target_creator,
            notification_type='user_engagement',
            title=f"New comment on your content",
            message=f"{action.actor.username} commented on your content",
            action=action,
            target_url=getattr(action.obj, 'get_absolute_url', lambda: None)()
        )
        return True
classDiagram
    class BaseNotificationStrategy {
        <<Abstract>>
        +get_recipients(obj) List~User~
        +create_notification_data(obj) dict
    }
    
    class ProjectNotificationStrategy {
        <<Abstract>>
        +_get_project_followers(project)
        +_get_project_initiators(project) List~User~
        +_get_project_moderators(project) List~User~
        +_get_project_recipients(project) List~User~
        +_get_event_recipients(event) List~User~
        +_get_phase_recipients(phase) List~User~
    }
    
    class CommentHighlighted {
        +get_recipients(comment) List~User~
        +create_notification_data(comment) dict
        +notification_type: MODERATOR_HIGHLIGHT
        +message_template: "A moderator highlighted your comment comment in project _project_"
        +recipient: comment_creator
    }
    
    class ProjectComment {
        +get_recipients(comment) List~User~
        +create_notification_data(comment) dict
        +notification_type: COMMENT_ON_POST
        +message_template: "user commented on your post _post_"
        +recipients: content_creator (excludes self)
    }
    
    class CommentReply {
        +get_recipients(comment) List~User~
        +create_notification_data(comment) dict
        +notification_type: COMMENT_REPLY
        +message_template: "user replied to your comment"
        +recipient: parent_comment_creator (excludes self)
    }
    
    BaseNotificationStrategy <|-- CommentHighlighted
    BaseNotificationStrategy <|-- CommentReply
    ProjectNotificationStrategy <|-- ProjectComment
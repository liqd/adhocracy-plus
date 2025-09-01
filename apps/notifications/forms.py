# notifications/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import NotificationSettings

class NotificationSettingsForm(forms.ModelForm):
    """
    Simplified form for notification settings with clean structure.
    """
    
    # Group toggles
    project_related_notifications = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Project related notifications"),
        widget=forms.CheckboxInput(attrs={'class': 'group-toggle'})
    )
    
    user_interactions_notifications = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Interactions with other users"),
        widget=forms.CheckboxInput(attrs={'class': 'group-toggle'})
    )
    
    class Meta:
        model = NotificationSettings
        fields = [
            # Project related notifications
            'email_newsletter',
            'email_project_updates',
            'notify_project_updates',
            'email_project_events',
            'notify_project_events',
            
            # User interactions
            'email_user_engagement',
            'notify_user_engagement',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_initial_group_toggles()
        self._setup_field_attributes()
    
    def _set_initial_group_toggles(self):
        """Set initial values for group toggles based on individual settings."""
        if self.instance.pk:
            # Project related group
            project_fields = ['email_newsletter', 'email_project_updates', 'notify_project_updates', 
                            'email_project_events', 'notify_project_events']
            self.fields['project_related_notifications'].initial = any(
                getattr(self.instance, field) for field in project_fields
            )
            
            # User interactions group
            user_fields = ['email_user_engagement', 'notify_user_engagement']
            self.fields['user_interactions_notifications'].initial = any(
                getattr(self.instance, field) for field in user_fields
            )
    
    def _setup_field_attributes(self):
        """Configure field labels and help texts."""
        field_config = {
            'email_newsletter': {
                'label': _("Email newsletter"),
                'help_text': _("Receive email newsletter with updates and news from projects you follow.")
            },
            'email_project_updates': {
                'label': _("Participation status"),
                'help_text': _("Receive a notification when participation starts in a project you follow.")
            },
            'notify_project_updates': {
                'label': "",  # Empty for In-App toggle
                'help_text': ""
            },
            'email_project_events': {
                'label': _("Events"),
                'help_text': _("Receive notifications about upcoming events in projects you follow.")
            },
            'notify_project_events': {
                'label': "",  # Empty for In-App toggle
                'help_text': ""
            },
            'email_user_engagement': {
                'label': _("Reactions from other users to your posts"),
                'help_text': _("Receive a notification when someone rates or comments on your post.")
            },
            'notify_user_engagement': {
                'label': "",  # Empty for In-App toggle
                'help_text': ""
            }
        }
        
        for field_name, config in field_config.items():
            self.fields[field_name].label = config['label']
            self.fields[field_name].help_text = config['help_text']
    
    def save(self, commit=True):
        """Handle group toggle logic."""
        instance = super().save(commit=False)
        
        # Disable all project-related settings if group is off
        if not self.cleaned_data.get('project_related_notifications', True):
            project_fields = ['email_newsletter', 'email_project_updates', 'notify_project_updates',
                            'email_project_events', 'notify_project_events']
            for field in project_fields:
                setattr(instance, field, False)
        
        # Disable all interaction settings if group is off
        if not self.cleaned_data.get('user_interactions_notifications', True):
            instance.email_user_engagement = False
            instance.notify_user_engagement = False
        
        if commit:
            instance.save()
        
        return instance
    
    def get_field_groups(self):
        """Return organized field groups for template rendering."""
        return {
            'project_related': {
                'title': _("Project related notifications"),
                'fields': self._get_project_related_fields()
            },
            'user_interactions': {
                'title': _("Interactions with other users"),
                'fields': self._get_user_interaction_fields()
            }
        }
    
    def _get_project_related_fields(self):
        """Return project-related fields in display order."""
        return [
            (self['email_newsletter'], _("Email newsletter"), _("Receive email newsletter with updates and news from projects you follow.")),
            (self['email_project_updates'], _("Participation status"), _("Receive a notification when participation starts in a project you follow.")),
            (self['notify_project_updates'], "", ""),
            (self['email_project_events'], _("Events"), _("Receive notifications about upcoming events in projects you follow.")),
            (self['notify_project_events'], "", "")
        ]
    
    def _get_user_interaction_fields(self):
        """Return user interaction fields in display order."""
        return [
            (self['email_user_engagement'], _("Reactions from other users to your posts"), _("Receive a notification when someone rates or comments on your post.")),
            (self['notify_user_engagement'], "", "")
        ]
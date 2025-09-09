from ..base import BaseNotificationStrategy
from ...models import NotificationType

class ProposalFeedbackStrategy(BaseNotificationStrategy):

    def get_in_app_recipients(self, proposal):
        recipients = set()
        if proposal.creator:
            # TODO: Check user preferences
            recipients.add(proposal.creator)
        
        return recipients
    
    def get_email_recipients(self, proposal):
        return self.get_in_app_recipients(proposal)
    
    def create_notification_data(self, proposal):
        from django.utils.translation import gettext_lazy as _
        return {
            'notification_type': NotificationType.MODERATOR_IDEA_FEEDBACK,
            'message_template': _("A moderator gave feedback on your proposal {proposal}"),
            'context': {
                'proposal_url': proposal.get_absolute_url(),
                'proposal': ideproposal.name,
            }
        }
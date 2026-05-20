from apps.users.emails import EmailAplus as Email
from apps.users.models import User


class NewsletterEmail(Email):
    """Email class for newsletter emails"""

    template_name = "a4_candy_newsletters/emails/newsletter_email"

    def __init__(self, newsletter, organisation, participant_ids):
        self._newsletter = newsletter
        self._organisation = organisation
        self._participant_ids = participant_ids

    def get_organisation(self):
        return self._organisation

    def get_receivers(self):
        return (
            User.objects.filter(id__in=self._participant_ids)
            .filter(get_newsletters=True)
            .filter(is_active=True)
            .distinct()
        )

    def get_reply_to(self):
        return [self._newsletter.sender]

    def get_context(self):
        context = super().get_context()
        context.update(
            {
                "newsletter": self._newsletter,
                "organisation": self._organisation,
            }
        )
        return context


class NewsletterEmailAll(NewsletterEmail):
    def get_receivers(self):
        return User.objects.filter(is_active=True).distinct()

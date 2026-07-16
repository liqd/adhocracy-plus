"""Wire adhocracy4 email classes into adhocracy-plus.

adhocracy4 ships some emails (e.g. report-to-moderator) on its base ``Email``
class, which does not use ``EmailAplus``. At startup we replace those classes
with ``EmailAplus`` subclasses so they pick up organisation-branded sender names
and other a+ behaviour (see ``apps/users/emails.py``).
"""


def patch_report_moderator_email():
    from adhocracy4.reports import emails as reports_emails
    from apps.users.emails import EmailAplus

    class ReportModeratorEmail(EmailAplus):
        template_name = "a4reports/emails/report_moderators"

        def get_organisation(self):
            return self.object.project.organisation

        def get_receivers(self):
            return self.object.project.moderators.all()

    reports_emails.ReportModeratorEmail = ReportModeratorEmail

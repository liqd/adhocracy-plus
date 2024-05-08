from apps.users.emails import EmailAplus as Email


class AccountDeletionEmail(Email):
    template_name = "a4_candy_account/emails/account_deleted"

    def get_receivers(self):
        return [self.object.email]

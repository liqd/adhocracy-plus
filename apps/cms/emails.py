from apps.users.emails import EmailAplus as Email


class AnswerToContactFormEmail(Email):
    template_name = 'a4_candy_cms_contacts/emails/answer_to_contact_form'

    def get_receivers(self):
        submission = self.object
        form_data = submission.get_data()
        if form_data.get('receive_copy'):
            return [form_data.get('email')]

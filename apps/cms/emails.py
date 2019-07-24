from apps.users.emails import EmailWithUserLanguage as Email


class AnswerToContactFormEmail(Email):
    template_name = 'a4_candy_cms_contacts/emails/answer_to_contact_form'

    def get_receivers(self):
        submission = self.object
        form_data = submission.get_data()
        if form_data.get('receive_copy'):
            return [form_data.get('email')]

    def get_context(self):
        context = super().get_context()
        submission = self.object
        form_data = submission.get_data()
        data_list = ['{}: {}'.format(key.replace('_', ' '), value)
                     for key, value in form_data.items()
                     if not type(value).__name__ == 'bool']
        context['data_list'] = data_list
        return context

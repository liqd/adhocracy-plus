from django.core import mail


def get_emails_for_address(email_address):
    """Return all mails send to email_address"""
    mails = list(filter(lambda mails: mails.to[0] == email_address, mail.outbox))
    return mails

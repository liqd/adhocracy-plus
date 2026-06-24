from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core import mail
from django.test import RequestFactory
from guest_user.functions import maybe_create_guest_user

User = get_user_model()


class GuestUserCreator:
    def __init__(self):
        self.request_factory = RequestFactory()

    def create_guest_user(self):
        request = self.request_factory.get("/")
        request.user = AnonymousUser()
        request.session = SessionStore()
        request.session.create()

        maybe_create_guest_user(request)
        return User.objects.latest("date_joined")


def get_emails_for_address(email_address):
    """Return all mails send to email_address"""
    mails = list(filter(lambda mails: mails.to[0] == email_address, mail.outbox))
    return mails

from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from guest_user.models import Guest


@receiver(email_confirmed)
def on_email_confirmed(request, email_address, **kwargs):
    """
    Delete Guest associated with guest Users
    """

    user = email_address.user
    Guest.objects.filter(user=user).delete()

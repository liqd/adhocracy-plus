# from datetime import timedelta

# import pytest
# from dateutil.parser import parse
# from django.core import mail
# from django.core.management import call_command
# from freezegun import freeze_time

# TODO: Replace test or remove file
# @pytest.mark.django_db
# def test_notify_follower_on_upcoming_event(offline_event_factory):
#     offline_event = offline_event_factory(
#         date=parse("2022-01-05 17:00:00 UTC"),
#     )

#     with freeze_time(offline_event.date - timedelta(minutes=30)):
#         call_command("create_offlineevent_system_actions")

#     assert len(mail.outbox) == 2
#     assert mail.outbox[1].subject.startswith("Event in project ")

import pytest
from django.contrib.admin import site
from django.contrib.admin.models import LogEntry
from django.test import RequestFactory
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _make_request(answer):
    url = reverse("admin:a4polls_answer_change", args=[answer.pk])
    request = RequestFactory().post(url)
    request.POST = request.POST.copy()
    request.POST.update(
        {
            "question": str(answer.question_id),
            "answer": "EDITED ANSWER TEXT",
            "_save": "Save",
        }
    )
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_superuser("admin", "a@b.de", "pw")
    request.user = user
    return request


def test_admin_change_logs_old_and_new_value(answer_factory):
    answer = answer_factory()
    answer.answer = "OLD ANSWER TEXT"
    answer.save()

    admin = site._registry[type(answer)]
    try:
        admin._changeform_view(_make_request(answer), str(answer.pk), None, None)
    except Exception:
        # Rendering the redirect's success message requires the messages
        # middleware, which is not installed in this test. The LogEntry is
        # already created before that point, so we continue.
        pass

    entry = LogEntry.objects.get(object_id=str(answer.pk), action_flag=2)
    assert "OLD ANSWER TEXT" in entry.change_message
    assert "EDITED ANSWER TEXT" in entry.change_message

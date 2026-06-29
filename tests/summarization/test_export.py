"""Tests for project export JSON serializability."""

import json

import pytest

from apps.summarization.export_utils.core import generate_full_export
from tests.offlineevents.factories import OfflineEventFactory


@pytest.mark.django_db
def test_generate_full_export_is_json_serializable_with_offline_events(project_factory):
    project = project_factory()
    OfflineEventFactory(project=project)

    export_data = generate_full_export(project)

    json.dumps(export_data, indent=2)

    offline_events = export_data.get("offline_events", [])
    assert len(offline_events) == 1
    assert isinstance(offline_events[0]["timeline_index"], int)

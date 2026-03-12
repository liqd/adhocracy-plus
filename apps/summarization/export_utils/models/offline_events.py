from ..processing.extractors import extract_attachments


def export_offline_event(event):
    """Export a single offline event."""
    return {
        "id": event.id,
        "name": event.name,
        "event_type": event.event_type,
        "date": event.date.isoformat(),
        "description": str(event.description),
        "attachments": extract_attachments(str(event.description)),
        "slug": event.slug,
        "url": event.get_absolute_url(),
        "timeline_index": event.get_timeline_index,
        # "created": event.created.isoformat(),
        "modified": event.modified.isoformat() if event.modified else None,
    }

from ..processing.extractors import extract_comments
from ..processing.extractors import extract_ratings


def export_topic(topic):
    """Export a single topic with all its data."""
    return {
        "id": topic.id,
        "name": topic.name,
        "description": str(topic.description),
        # "created": topic.created.isoformat(),
        "reference_number": topic.reference_number,
        "category": topic.category.name if topic.category else None,
        "labels": [label.name for label in topic.labels.all()],
        "comment_count": topic.comments.count(),
        "comments": extract_comments(topic.comments.all()),
        "rating_count": topic.ratings.count(),
        "ratings": extract_ratings(topic.ratings.all()),
    }

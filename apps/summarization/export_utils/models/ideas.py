from ..processing.extractors import extract_attachments
from ..processing.extractors import extract_comments
from ..processing.extractors import extract_ratings


def export_idea(idea):
    """Export a single idea with all its data."""
    return {
        "id": idea.id,
        "name": idea.name,
        "description": str(idea.description),
        "attachments": extract_attachments(str(idea.description)),
        # "created": idea.created.isoformat(),
        "reference_number": idea.reference_number,
        "category": idea.category.name if idea.category else None,
        "labels": [label.name for label in idea.labels.all()],
        "comment_count": idea.comments.count(),
        "comments": extract_comments(idea.comments.all()),
        "rating_count": idea.ratings.count(),
        "ratings": extract_ratings(idea.ratings.all()),
        "images": [i.name for i in idea._a4images_current_images],
    }

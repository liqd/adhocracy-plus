from ..processing.extractors import extract_attachments
from ..processing.extractors import extract_comments
from ..processing.extractors import extract_ratings


def export_proposal(proposal):
    """Export a single participatory budgeting proposal with all its data."""

    point = None
    if proposal.point:
        if hasattr(proposal.point, "y"):  # It's a Point object
            point = {
                "lat": proposal.point.y,
                "lng": proposal.point.x,
            }
        elif isinstance(proposal.point, dict):  # It's already a dict
            point = {
                "lat": proposal.point.get("y") or proposal.point.get("lat"),
                "lng": proposal.point.get("x") or proposal.point.get("lng"),
            }

    return {
        "id": proposal.id,
        "name": proposal.name,
        "description": str(proposal.description),
        "attachments": extract_attachments(str(proposal.description)),
        # "created": proposal.created.isoformat(),
        "reference_number": proposal.reference_number,
        "category": proposal.category.name if proposal.category else None,
        "labels": [label.name for label in proposal.labels.all()],
        "comment_count": proposal.comments.count(),
        "comments": extract_comments(proposal.comments.all()),
        "rating_count": proposal.ratings.count(),
        "ratings": extract_ratings(proposal.ratings.all()),
        "budget": proposal.budget,
        "point": point,
        "point_label": proposal.point_label,
    }

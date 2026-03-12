from ..processing.extractors import extract_comments


def export_debate(debate):
    """Export a single debate subject with all its data."""
    return {
        "id": debate.id,
        "name": debate.name,
        "description": debate.description,
        # "created": debate.created.isoformat(),
        "reference_number": debate.reference_number,
        "slug": debate.slug,
        "comment_count": debate.comments.count(),
        "comments": extract_comments(debate.comments.all()),
        "comment_creator_count": debate.comment_creator_count,
    }

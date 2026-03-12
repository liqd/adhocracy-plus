import re


def extract_attachments(text):
    """Extract upload links from HTML text"""
    if not text:
        return []

    # Find all links containing /uploads/ (both href and src attributes)
    pattern_href = r'href="([^"]*?/uploads/[^"]*?)"'
    pattern_src = r'src="([^"]*?/uploads/[^"]*?)"'

    attachments_href = re.findall(pattern_href, text)
    attachments_src = re.findall(pattern_src, text)

    # Combine and deduplicate
    attachments = list(dict.fromkeys(attachments_href + attachments_src))

    return attachments


def extract_comments(queryset, include_ratings=True, include_children=True):
    """
    Extract comments from any model with a 'comments' GenericRelation.
    Filters out removed, censored, or blocked comments.
    Recursively includes child comments.

    Args:
        queryset: Comment queryset (e.g., obj.comments.all())
        include_ratings: Whether to include ratings on comments
        include_children: Whether to recursively include child comments

    Returns:
        List of comment dictionaries with nested 'replies' key
    """
    comments_list = []

    # Filter out unwanted comments at the queryset level
    filtered_queryset = queryset.filter(
        is_removed=False, is_censored=False, is_blocked=False
    )

    for comment in filtered_queryset:
        comment_data = {
            "id": comment.id,
            "text": comment.comment,
            # "created": comment.created.isoformat(),
        }

        # Optional fields
        if hasattr(comment, "comment_categories") and comment.comment_categories:
            comment_data["comment_categories"] = comment.comment_categories

        if include_ratings and hasattr(comment, "ratings"):
            comment_data["ratings"] = [
                {
                    "id": rating.id,
                    "value": rating.value,
                }
                for rating in comment.ratings.all()
            ]

        # Recursively include child comments (they will also be filtered)
        if include_children and hasattr(comment, "child_comments"):
            child_comments = comment.child_comments.all()
            if child_comments.exists():
                comment_data["replies"] = extract_comments(
                    child_comments,
                    include_ratings=include_ratings,
                    include_children=True,
                )
                comment_data["reply_count"] = len(comment_data["replies"])

        comments_list.append(comment_data)

    return comments_list


def extract_ratings(queryset):
    """
    Extract ratings from any model with a 'ratings' GenericRelation.

    Args:
        queryset: Rating queryset (e.g., obj.ratings.all())

    Returns:
        List of rating dictionaries
    """
    ratings_list = []
    for rating in queryset:
        ratings_list.append(
            {
                "id": rating.id,
                "value": rating.value,
            }
        )
    return ratings_list

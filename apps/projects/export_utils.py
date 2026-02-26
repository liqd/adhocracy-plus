import re

# import json
from adhocracy4.comments.models import Comment
from adhocracy4.polls.models import Poll
from apps.debate.models import Subject
from apps.documents.models import Chapter
from apps.documents.models import Paragraph
from apps.ideas.models import Idea
from apps.offlineevents.models import OfflineEvent
from apps.topicprio.models import Topic


def get_module_status(module):
    """
    Return the status of a module based on its phases.

    Returns:
        str: 'past', 'active', or 'future'
    """

    # Use the existing queryset methods
    try:
        if module.module_has_finished:
            return "past"
        elif module.active_phase:
            return "active"
        else:
            return "future"
    except (TypeError, ValueError):
        # Fallback if module_has_finished or active_phase fail due to None datetime values
        return "future"


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
    Recursively includes child comments.

    Args:
        queryset: Comment queryset (e.g., obj.comments.all())
        include_ratings: Whether to include ratings on comments
        include_children: Whether to recursively include child comments

    Returns:
        List of comment dictionaries with nested 'replies' key
    """
    comments_list = []

    for comment in queryset:
        comment_data = {
            "id": comment.id,
            "text": comment.comment,
            "created": comment.created.isoformat(),
            "is_removed": comment.is_removed,
            "is_censored": comment.is_censored,
            "is_blocked": comment.is_blocked,
        }

        # Optional fields
        if hasattr(comment, "comment_categories") and comment.comment_categories:
            comment_data["comment_categories"] = comment.comment_categories
        if hasattr(comment, "is_moderator_marked"):
            comment_data["is_moderator_marked"] = comment.is_moderator_marked
        if hasattr(comment, "is_reviewed"):
            comment_data["is_reviewed"] = comment.is_reviewed

        if include_ratings and hasattr(comment, "ratings"):
            comment_data["ratings"] = [
                {
                    "id": rating.id,
                    "value": rating.value,
                }
                for rating in comment.ratings.all()
            ]

        # Recursively include child comments
        if include_children and hasattr(comment, "child_comments"):
            child_comments = comment.child_comments.all()
            if child_comments.exists():
                comment_data["replies"] = extract_comments(
                    child_comments,
                    include_ratings=include_ratings,
                    include_children=True,
                )
                comment_data["reply_count"] = child_comments.count()

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
                "created": rating.created.isoformat(),
            }
        )
    return ratings_list


def create_module_base(item):
    """Create base module structure"""
    return {
        "module_id": item["module_id"],
        "module_name": item["module_name"],
        "module_type": get_module_type_from_name(item["module_name"]),
        "phase_status": item["active_status"],
        "module_order": 0,
        "link": None,
        "signals": {
            "has_comments": False,
            "has_votes": False,
            "has_ratings": False,
            "has_open_answers": False,
            "has_base_text": False,
        },
        "counts": {
            "ideas": 0,
            "comments": 0,
            "votes": 0,
            "ratings": 0,
            "open_answers": 0,
        },
        "content": {},
        "meta": {
            "module_start": item["module_start"],
            "module_end": item["module_end"],
        },
    }


def process_ideas(module, item):
    """Process an idea item"""
    module["counts"]["ideas"] += 1
    module["counts"]["comments"] += item["comment_count"]
    module["counts"]["ratings"] += item["rating_count"]
    if item["comment_count"]:
        module["signals"]["has_comments"] = True
    if item["rating_count"]:
        module["signals"]["has_ratings"] = True
    module["content"].setdefault("ideas", []).append(item)


def process_polls(module, item):
    """Process a poll item"""
    module["counts"]["votes"] += item["total_votes"]
    module["counts"]["comments"] += item["comment_count"]
    if item["comment_count"]:
        module["signals"]["has_comments"] = True
    if item["total_votes"]:
        module["signals"]["has_votes"] = True
    module["content"].setdefault("questions", []).extend(item["questions"])
    module["content"]["description"] = item.get("description", "")
    module["content"]["comments"] = item.get("comments", [])


def process_topics(module, item):
    """Process a topic item"""
    module["counts"]["comments"] += item["comment_count"]
    module["counts"]["ratings"] += item["rating_count"]
    if item["comment_count"]:
        module["signals"]["has_comments"] = True
    if item["rating_count"]:
        module["signals"]["has_ratings"] = True
    module["content"].setdefault("topics", []).append(item)


def process_debates(module, item):
    """Process a debate item"""
    module["counts"]["comments"] += item["comment_count"]
    if item["comment_count"]:
        module["signals"]["has_comments"] = True
    module["content"].setdefault("debates", []).append(item)


def process_documents(module, item):
    """Process a document chapter"""
    if item not in module["content"].get("chapters", []):
        module["content"].setdefault("chapters", []).append(item)


def group_by_module(export_data):
    """Group all items by module and organize them into past/current/upcoming sections."""
    modules_by_id = {}

    # Define item type handlers
    handlers = {
        "ideas": process_ideas,
        "polls": process_polls,
        "topics": process_topics,
        "debates": process_debates,
        "documents": process_documents,
    }

    # Collect all items by module
    for item_type, items in [
        ("ideas", export_data.get("ideas", [])),
        ("polls", export_data.get("polls", [])),
        ("topics", export_data.get("topics", [])),
        ("debates", export_data.get("debates", [])),
        ("documents", export_data.get("documents", [])),
    ]:
        handler = handlers.get(item_type)
        if not handler:
            continue

        for item in items:
            module_id = item["module_id"]
            if module_id not in modules_by_id:
                modules_by_id[module_id] = create_module_base(item)

            handler(modules_by_id[module_id], item)

    # Organize by status
    result = {
        "project": export_data["project"],
        "stats": export_data["stats"],
        "phases": {
            "past": {"phase_status": "past", "modules": []},
            "current": {"phase_status": "current", "modules": []},
            "upcoming": {"phase_status": "upcoming", "modules": []},
        },
    }

    # Group modules by status
    status_map = {"past": "past", "active": "current", "future": "upcoming"}
    for module in modules_by_id.values():
        phase = status_map.get(module["phase_status"])
        if phase:
            result["phases"][phase]["modules"].append(module)

    return result


def get_module_type_from_name(module_name):
    """Map module name to blueprint type"""
    module_type_map = {
        "brainstorming": "brainstorming",
        "map-brainstorming": "map-brainstorming",
        "idea-challenge": "idea-collection",
        "spatial-idea-challenge": "map-idea-collection",
        "text-review": "text-review",
        "poll": "poll",
        "participatory-budgeting": "participatory-budgeting",
        "interactive-event": "interactive-event",
        "topic-prioritization": "topic-prioritization",
        "debate": "debate",
    }
    name_lower = module_name.lower().replace(" ", "-")
    return module_type_map.get(name_lower, "unknown")


def generate_full_export(project):
    """Generate complete project export data"""
    description_attachments = extract_attachments(project.description)
    information_attachments = (
        extract_attachments(project.information)
        if hasattr(project, "information")
        else []
    )
    result_attachments = extract_attachments(project.result)

    export = {
        "project": {
            "name": project.name,
            "description": project.description,
            "description_attachments": description_attachments,
            "information": (
                project.information if hasattr(project, "information") else None
            ),
            "information_attachments": information_attachments,
            "slug": project.slug,
            "organisation": project.organisation.name,
            "result": project.result,
            "result_attachments": result_attachments,
            "url": project.get_absolute_url(),
        },
        "ideas": export_ideas_full(project),
        "polls": export_polls_full(project),
        "topics": export_topics_full(project),
        "debates": export_debates_full(project),
        "documents": export_documents_full(project),
        "offline_events": export_offline_events_full(project),
        "stats": calculate_stats(project),
    }
    structured = group_by_module(export)
    # print(json.dumps(structured))
    return structured


def export_ideas_full(project):
    """Export all ideas with full data"""
    ideas_data = []
    ideas = (
        Idea.objects.filter(module__project=project)
        .select_related("category")
        .prefetch_related("labels")
    )

    for idea in ideas:
        # Get comments for this idea
        comments_list = extract_comments(idea.comments.all())

        # Get ratings for this idea
        ratings_list = extract_ratings(idea.ratings.all())

        ideas_data.append(
            {
                "id": idea.id,
                "active_status": get_module_status(idea.module),
                "module_start": str(idea.module.module_start),
                "module_end": str(idea.module.module_end),
                "url": idea.get_absolute_url(),
                "name": idea.name,
                "description": str(idea.description),
                "attachments": extract_attachments(str(idea.description)),
                "created": idea.created.isoformat(),
                "reference_number": idea.reference_number,
                "category": idea.category.name if idea.category else None,
                "labels": [label.name for label in idea.labels.all()],
                "comment_count": idea.comments.count(),
                "comments": comments_list,
                "rating_count": idea.ratings.count(),
                "ratings": ratings_list,
                "module_id": idea.module.id,
                "module_name": idea.module.name,
                "images": [i.name for i in idea._a4images_current_images],
            }
        )

    return ideas_data


def export_polls_full(project):
    """Export all polls with full data"""

    polls_data = []
    polls = Poll.objects.filter(module__project=project).prefetch_related(
        "questions__choices__votes__other_vote",
    )

    for poll in polls:
        questions_list = []
        for question in poll.questions.all().order_by("weight"):
            choices_list = []
            for choice in question.choices.all().order_by("weight"):
                votes_list = []
                for vote in choice.votes.all():
                    vote_data = {
                        "created": vote.created.isoformat(),
                    }
                    if hasattr(vote, "other_vote"):
                        vote_data["other_answer"] = vote.other_vote.answer
                    votes_list.append(vote_data)

                choices_list.append(
                    {
                        "label": choice.label,
                        "is_other_choice": choice.is_other_choice,
                        "vote_count": choice.votes.count(),
                        "votes": votes_list,
                    }
                )

            answers_list = []
            for answer in question.answers.all():
                answers_list.append(
                    {
                        "answer": answer.answer,
                        "created": answer.created.isoformat(),
                    }
                )

            questions_list.append(
                {
                    "label": question.label,
                    "multiple_choice": question.multiple_choice,
                    "is_open": question.is_open,
                    "choices": choices_list,
                    "answers": answers_list,
                    "vote_count": sum(c["vote_count"] for c in choices_list),
                }
            )

        # Get comments for this poll
        comments_list = extract_comments(poll.comments.all())

        polls_data.append(
            {
                "id": poll.id,
                "module_id": poll.module.id,
                "active_status": get_module_status(poll.module),
                "module_start": str(poll.module.module_start),
                "module_end": str(poll.module.module_end),
                "description": poll.module.description,
                "url": poll.get_absolute_url(),
                "module_name": poll.module.name,
                "questions": questions_list,
                "comments": comments_list,
                "comment_count": poll.comments.count(),
                "total_votes": sum(q["vote_count"] for q in questions_list),
            }
        )

    return polls_data


def export_topics_full(project):
    """Export all topics with full data"""

    topics_data = []
    topics = (
        Topic.objects.filter(module__project=project)
        .select_related("category")
        .prefetch_related("labels")
    )

    for topic in topics:
        # Get comments for this topic
        comments_list = extract_comments(topic.comments.all())

        # Get ratings for this topic
        ratings_list = extract_ratings(topic.ratings.all())

        topics_data.append(
            {
                "id": topic.id,
                "active_status": get_module_status(topic.module),
                "module_start": str(topic.module.module_start),
                "module_end": str(topic.module.module_end),
                "url": topic.get_absolute_url(),
                "name": topic.name,
                "description": str(topic.description),
                "created": topic.created.isoformat(),
                "reference_number": topic.reference_number,
                "category": topic.category.name if topic.category else None,
                "labels": [label.name for label in topic.labels.all()],
                "comment_count": topic.comments.count(),
                "comments": comments_list,
                "rating_count": topic.ratings.count(),
                "ratings": ratings_list,
                "module_id": topic.module.id,
                "module_name": topic.module.name,
            }
        )

    return topics_data


def export_documents_full(project):
    """Export all document chapters and paragraphs with comments"""

    documents_data = []
    chapters = Chapter.objects.filter(module__project=project)

    for chapter in chapters:
        # Get chapter comments
        chapter_comments = extract_comments(chapter.comments.all())

        # Get paragraphs for this chapter
        paragraphs_list = []
        for paragraph in chapter.paragraphs.all().order_by("weight"):
            # Get paragraph comments
            paragraph_comments = extract_comments(paragraph.comments.all())

            paragraphs_list.append(
                {
                    "id": paragraph.id,
                    "name": paragraph.name,
                    "text": str(paragraph.text),
                    "attachments": extract_attachments(str(paragraph.text)),
                    "weight": paragraph.weight,
                    "created": paragraph.created.isoformat(),
                    "comment_count": paragraph.comments.count(),
                    "comments": paragraph_comments,
                }
            )

        documents_data.append(
            {
                "id": chapter.id,
                "name": chapter.name,
                "url": chapter.get_absolute_url(),
                "weight": chapter.weight,
                "created": chapter.created.isoformat(),
                "active_status": get_module_status(chapter.module),
                "module_start": str(chapter.module.module_start),
                "module_end": str(chapter.module.module_end),
                "module_id": chapter.module.id,
                "module_name": chapter.module.name,
                "prev_chapter_id": chapter.prev.id if chapter.prev else None,
                "next_chapter_id": chapter.next.id if chapter.next else None,
                "paragraph_count": chapter.paragraphs.count(),
                "paragraphs": paragraphs_list,
                "chapter_comment_count": chapter.comments.count(),
                "chapter_comments": chapter_comments,
                "total_paragraph_comments": sum(
                    p["comment_count"] for p in paragraphs_list
                ),
            }
        )

    return documents_data


def collect_document_attachments(export_data, request):
    """
    Collect all document attachments from project fields (information, result).

    Args:
        export_data: The full export dictionary (as returned by generate_full_export())
        request: Django Request object for build_absolute_uri()

    Returns:
        tuple: (documents_dict, handle_to_source)
            - documents_dict: {handle: absolute_url, ...}
            - handle_to_source: {handle: "project_information" | "project_result", ...}
    """
    documents_dict = {}
    handle_to_source = {}

    project_data = export_data.get("project", {})

    # Collect attachments from information field
    information_attachments = project_data.get("information_attachments", [])
    for attachment_index, attachment_url in enumerate(information_attachments):
        handle = f"project_information_attachment_{attachment_index}"
        absolute_url = request.build_absolute_uri(attachment_url)
        documents_dict[handle] = absolute_url
        handle_to_source[handle] = "project_information"

    # Collect attachments from result field
    result_attachments = project_data.get("result_attachments", [])
    for attachment_index, attachment_url in enumerate(result_attachments):
        handle = f"project_result_attachment_{attachment_index}"
        absolute_url = request.build_absolute_uri(attachment_url)
        documents_dict[handle] = absolute_url
        handle_to_source[handle] = "project_result"

    return documents_dict, handle_to_source


def integrate_document_summaries(
    export_data: dict,
    document_summaries: list,
    handle_to_source: dict[str, str],
):
    """
    Integrate document summaries into export_data by project field source.

    Args:
        export_data: Export dictionary (modified in-place)
        document_summaries: List of DocumentSummaryItem objects
        handle_to_source: Mapping from handle to source field ("project_information", "project_result")
    """
    # Initialize document_summaries structure
    project_summaries = {
        "information": [],
        "result": [],
    }

    # Group summaries by source field
    for summary_item in document_summaries:
        handle = summary_item.handle
        source = handle_to_source.get(handle)

        if source == "project_information":
            project_summaries["information"].append(
                {
                    "handle": summary_item.handle,
                    "summary": summary_item.summary,
                }
            )
        elif source == "project_result":
            project_summaries["result"].append(
                {
                    "handle": summary_item.handle,
                    "summary": summary_item.summary,
                }
            )

    # Integrate summaries into export_data
    if "project" not in export_data:
        export_data["project"] = {}
    export_data["project"]["document_summaries"] = project_summaries


def export_debates_full(project):
    """Export all debate subjects with comments"""

    debates_data = []
    subjects = Subject.objects.filter(module__project=project)

    for subject in subjects:
        # Get comments for this subject
        comments_list = extract_comments(subject.comments.all())

        debates_data.append(
            {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "created": subject.created.isoformat(),
                "reference_number": subject.reference_number,
                "slug": subject.slug,
                "active_status": get_module_status(subject.module),
                "module_start": str(subject.module.module_start),
                "module_end": str(subject.module.module_end),
                "module_id": subject.module.id,
                "module_name": subject.module.name,
                "comment_count": subject.comments.count(),
                "comments": comments_list,
                "comment_creator_count": subject.comment_creator_count,
            }
        )

    return debates_data


def export_offline_events_full(project):
    """Export all offline events for a project"""

    events_data = []
    events = OfflineEvent.objects.filter(project=project)

    for event in events:
        events_data.append(
            {
                "id": event.id,
                "name": event.name,
                "event_type": event.event_type,
                "date": event.date.isoformat(),
                "description": str(event.description),
                "attachments": extract_attachments(str(event.description)),
                "slug": event.slug,
                "url": event.get_absolute_url(),
                "timeline_index": event.get_timeline_index,
                "created": event.created.isoformat(),
                "modified": event.modified.isoformat() if event.modified else None,
            }
        )

    return events_data


def calculate_stats(project):
    """Calculate statistics for the export"""
    # Get counts
    ideas_count = Idea.objects.filter(module__project=project).count()
    polls_count = Poll.objects.filter(module__project=project).count()
    topics_count = Topic.objects.filter(module__project=project).count()
    debates = Subject.objects.filter(module__project=project)
    chapters_count = Chapter.objects.filter(module__project=project).count()

    # Get paragraph count
    paragraphs_count = sum(
        chapter.paragraphs.count()
        for chapter in Chapter.objects.filter(module__project=project)
    )

    # Count comments on chapters
    chapter_comments_count = Comment.objects.filter(
        content_type__model="chapter",
        object_pk__in=Chapter.objects.filter(module__project=project).values_list(
            "id", flat=True
        ),
    ).count()

    # Count comments on paragraphs
    paragraph_comments_count = Comment.objects.filter(
        content_type__model="paragraph",
        object_pk__in=Paragraph.objects.filter(
            chapter__module__project=project
        ).values_list("id", flat=True),
    ).count()

    # Get comment counts
    ideas_comments = (
        sum(
            Idea.objects.get(pk=idea.id).comments.count()
            for idea in Idea.objects.filter(module__project=project)
        )
        if ideas_count > 0
        else 0
    )

    polls_comments = (
        sum(
            Poll.objects.get(pk=poll.id).comments.count()
            for poll in Poll.objects.filter(module__project=project)
        )
        if polls_count > 0
        else 0
    )

    topics_comments = (
        sum(
            Topic.objects.get(pk=topic.id).comments.count()
            for topic in Topic.objects.filter(module__project=project)
        )
        if topics_count > 0
        else 0
    )

    total_debate_comments = sum(debate.comments.count() for debate in debates)
    total_document_comments = chapter_comments_count + paragraph_comments_count
    total_comments = (
        ideas_comments
        + polls_comments
        + topics_comments
        + total_document_comments
        + total_debate_comments
    )

    return {
        "total_ideas": ideas_count,
        "total_polls": polls_count,
        "total_topics": topics_count,
        "total_debates": debates.count(),
        "total_comments": total_comments,
        "total_chapters": chapters_count,
        "total_paragraphs": paragraphs_count,
        "total_participants": project.participants.count(),
    }

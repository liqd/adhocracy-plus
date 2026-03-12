from apps.documents.models import Chapter

from ..processing.extractors import extract_attachments
from ..processing.extractors import extract_comments


def export_paragraph(paragraph):
    """Export a single paragraph."""
    return {
        "id": paragraph.id,
        "name": paragraph.name,
        "text": str(paragraph.text),
        "attachments": extract_attachments(str(paragraph.text)),
        "weight": paragraph.weight,
        # "created": paragraph.created.isoformat(),
        "comment_count": paragraph.comments.count(),
        "comments": extract_comments(paragraph.comments.all()),
    }


def export_document_chapters(module):
    """Export all chapters and paragraphs for a module."""
    chapters_data = []
    chapters = Chapter.objects.filter(module=module).order_by("weight")

    for chapter in chapters:
        chapters_data.append(
            {
                "id": chapter.id,
                "name": chapter.name,
                "url": chapter.get_absolute_url(),
                "weight": chapter.weight,
                # "created": chapter.created.isoformat(),
                "prev_chapter_id": chapter.prev.id if chapter.prev else None,
                "next_chapter_id": chapter.next.id if chapter.next else None,
                "paragraph_count": chapter.paragraphs.count(),
                "paragraphs": [
                    export_paragraph(p)
                    for p in chapter.paragraphs.all().order_by("weight")
                ],
                "chapter_comment_count": chapter.comments.count(),
                "chapter_comments": extract_comments(chapter.comments.all()),
            }
        )

    return chapters_data

import re
from datetime import datetime
from typing import List
from typing import Optional

from django.utils.html import strip_tags


def html_field_has_meaningful_content(value: Optional[str]) -> bool:
    """True if a CKEditor/HTML field has non-whitespace text."""
    if not value:
        return False
    text = strip_tags(value)
    text = re.sub(r"&nbsp;|\s", "", text)
    return len(text) > 0


def project_has_result_content(project) -> bool:
    return html_field_has_meaningful_content(project.result)


def get_last_online_participation_end(project) -> Optional[datetime]:
    """
    Latest phase end among non-draft modules.
    None if there is no such module or no dated phases.
    """
    end_candidates: List[datetime] = []
    for module in project.module_set.all():
        if module.is_draft:
            continue
        phase_ends = [
            p.end_date for p in module.phase_set.all() if p.end_date is not None
        ]
        if not phase_ends:
            continue
        end_candidates.append(max(phase_ends))
    if not end_candidates:
        return None
    return max(end_candidates)

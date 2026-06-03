from django.utils.html import strip_tags


def project_has_result_content(project) -> bool:
    return bool(strip_tags(project.result or "").strip())

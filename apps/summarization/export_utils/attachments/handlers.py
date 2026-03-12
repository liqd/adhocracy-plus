def _make_absolute_url(attachment_url, request=None, base_url=None):
    """Build absolute URL from attachment_url using request or base_url."""
    if request is not None:
        return request.build_absolute_uri(attachment_url)
    if base_url:
        base = base_url.rstrip("/")
        path = (
            attachment_url
            if attachment_url.startswith("/")
            else f"/{attachment_url.lstrip('/')}"
        )
        return f"{base}{path}"
    return None


def collect_document_attachments(export_data, request=None, base_url=None):
    """
    Collect all document attachments from project fields (information, result).

    Args:
        export_data: The full export dictionary (as returned by generate_full_export())
        request: Optional Django Request object for build_absolute_uri(). If None, base_url is used.
        base_url: Optional base URL (e.g. settings.WAGTAILADMIN_BASE_URL) when request is None.

    Returns:
        tuple: (documents_dict, handle_to_source)
            - documents_dict: {handle: absolute_url, ...}
            - handle_to_source: {handle: "project_information" | "project_result", ...}
    """
    documents_dict = {}
    handle_to_source = {}

    if request is None and not base_url:
        return documents_dict, handle_to_source

    project_data = export_data.get("project", {})

    # Collect attachments from information field
    information_attachments = project_data.get("information_attachments", [])
    for attachment_index, attachment_url in enumerate(information_attachments):
        handle = f"project_information_attachment_{attachment_index}"
        absolute_url = _make_absolute_url(
            attachment_url, request=request, base_url=base_url
        )
        if absolute_url:
            documents_dict[handle] = absolute_url
            handle_to_source[handle] = "project_information"

    # Collect attachments from result field
    result_attachments = project_data.get("result_attachments", [])
    for attachment_index, attachment_url in enumerate(result_attachments):
        handle = f"project_result_attachment_{attachment_index}"
        absolute_url = _make_absolute_url(
            attachment_url, request=request, base_url=base_url
        )
        if absolute_url:
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

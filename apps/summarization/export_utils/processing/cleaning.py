def clean_dict(data):
    """Remove empty/null values from a dictionary recursively."""
    if not isinstance(data, dict):
        return data

    cleaned = {}
    for key, value in data.items():
        # Skip None values
        if value is None:
            continue

        # Skip empty lists
        if isinstance(value, list) and len(value) == 0:
            continue

        # Skip empty strings
        if isinstance(value, str) and value == "":
            continue

        # Recursively clean nested dicts
        if isinstance(value, dict):
            cleaned_value = clean_dict(value)
            if cleaned_value:  # Only include non-empty dicts
                cleaned[key] = cleaned_value
        else:
            cleaned[key] = value

    return cleaned


def clean_comment(comment):
    """Clean a comment by removing redundant fields."""
    cleaned = {
        "id": comment["id"],
        "text": comment["text"],
    }

    # Only include replies if they exist
    if comment.get("replies"):
        cleaned["replies"] = [clean_comment(r) for r in comment["replies"]]
        cleaned["reply_count"] = len(cleaned["replies"])

    # Only include ratings if they exist
    if comment.get("ratings"):
        cleaned["ratings"] = comment["ratings"]

    return cleaned


def clean_content_item(item):  # noqa: C901
    """Clean a content item (idea, poll, etc.) by removing empty fields."""
    cleaned = {}

    # Always include essential fields
    for field in ["id", "name", "description", "created", "reference_number"]:
        if field in item:
            cleaned[field] = item[field]

    # Optional fields only if they have values
    if item.get("category"):
        cleaned["category"] = item["category"]

    if item.get("labels"):
        cleaned["labels"] = item["labels"]

    if item.get("attachments"):
        cleaned["attachments"] = item["attachments"]

    if item.get("images") and item["images"] != [""]:
        cleaned["images"] = item["images"]

    # Clean comments
    if item.get("comments"):
        cleaned["comments"] = [clean_comment(c) for c in item["comments"]]

    # Clean ratings
    if item.get("ratings"):
        cleaned["ratings"] = item["ratings"]

    # Poll-specific fields
    if item.get("choices"):
        cleaned["choices"] = item["choices"]
    if item.get("answers"):
        cleaned["answers"] = item["answers"]
    if item.get("other_answers"):
        cleaned["other_answers"] = item["other_answers"]

    # Map-specific fields
    if item.get("point") and (item["point"].get("lat") or item["point"].get("lng")):
        cleaned["point"] = item["point"]
    if item.get("point_label"):
        cleaned["point_label"] = item["point_label"]

    return cleaned


def clean_export(export_data):
    """Clean the entire export by removing empty/null values."""
    cleaned = {
        "project": clean_dict(export_data["project"]),  # Keep this for project
        "phases": {},
        "offline_events": export_data.get("offline_events", []),
    }

    # Clean each phase
    for phase_name, phase_data in export_data["phases"].items():
        cleaned_phase = {"phase_status": phase_data["phase_status"], "modules": []}

        for module in phase_data["modules"]:
            cleaned_module = {
                "module_id": module["module_id"],
                "module_name": module["module_name"],
                "module_type": module["module_type"],
                "module_start": module["module_start"],
                "module_end": module["module_end"],
                "url": module["url"],
                "content": {},
            }

            # Only include description if it exists
            if module.get("description"):
                cleaned_module["description"] = module["description"]

            # Clean each content type
            for content_type, items in module["content"].items():
                if items:
                    cleaned_module["content"][content_type] = [
                        clean_content_item(item) for item in items
                    ]

            cleaned_phase["modules"].append(cleaned_module)  # Remove clean_dict

        cleaned["phases"][phase_name] = cleaned_phase

    return cleaned  # Remove final clean_dict

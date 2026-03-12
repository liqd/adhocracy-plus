from .module_utils import get_module_type_from_name


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


def group_by_module(export_data):
    """Group all items by module and organize them into past/current/upcoming sections."""
    modules_by_id = {}

    # Define item type handlers
    handlers = {
        "ideas": process_ideas,
        "mapideas": process_mapideas,
        "polls": process_polls,
        "proposals": process_proposals,
        "topics": process_topics,
        "debates": process_debates,
        "documents": process_documents,
    }

    # Collect all items by module
    for item_type, items in [
        ("ideas", export_data.get("ideas", [])),
        ("mapideas", export_data.get("mapideas", [])),
        ("polls", export_data.get("polls", [])),
        ("topics", export_data.get("topics", [])),
        ("proposals", export_data.get("proposals", [])),
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
        else:
            print(
                f"WARNING: Unknown phase_status '{module['phase_status']}' for module {module['module_name']}"
            )

    return result


def restructure_by_phase(export_data):
    """Restructure modules array into phases object with past/current/upcoming."""
    phases = {
        "past": {"phase_status": "past", "modules": []},
        "current": {"phase_status": "current", "modules": []},
        "upcoming": {"phase_status": "upcoming", "modules": []},
    }

    status_map = {"past": "past", "active": "current", "future": "upcoming"}

    for module in export_data.get("modules", []):
        phase = status_map.get(module["active_status"])
        if phase:
            # Remove active_status from module since it's now at phase level
            module_copy = module.copy()
            module_copy.pop("active_status", None)
            phases[phase]["modules"].append(module_copy)

    return {
        "project": export_data["project"],
        "phases": phases,
        "offline_events": export_data.get("offline_events", []),
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


def process_mapideas(module, item):
    """Process a map idea item (same as regular ideas)"""
    module["counts"]["ideas"] += 1
    module["counts"]["comments"] += item["comment_count"]
    module["counts"]["ratings"] += item["rating_count"]
    if item["comment_count"]:
        module["signals"]["has_comments"] = True
    if item["rating_count"]:
        module["signals"]["has_ratings"] = True
    module["content"].setdefault("mapideas", []).append(item)


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


def process_proposals(module, item):
    """Process a proposal item (similar to ideas but with budget)."""
    module["counts"]["ideas"] += 1
    module["counts"]["comments"] += item["comment_count"]
    module["counts"]["ratings"] += item["rating_count"]
    if item["comment_count"]:
        module["signals"]["has_comments"] = True
    if item["rating_count"]:
        module["signals"]["has_ratings"] = True
    module["content"].setdefault("proposals", []).append(item)


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

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

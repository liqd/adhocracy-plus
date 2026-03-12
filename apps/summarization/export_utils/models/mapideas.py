from .ideas import export_idea


def export_mapidea(mapidea):
    """Export a single map idea with all its data."""
    data = export_idea(mapidea)  # Reuse base idea export

    # Handle point - could be Point object or dict
    point = None
    if mapidea.point:
        if hasattr(mapidea.point, "y"):  # It's a Point object
            point = {
                "lat": mapidea.point.y,
                "lng": mapidea.point.x,
            }
        elif isinstance(mapidea.point, dict):  # It's already a dict
            point = {
                "lat": mapidea.point.get("y") or mapidea.point.get("lat"),
                "lng": mapidea.point.get("x") or mapidea.point.get("lng"),
            }

    data.update(
        {
            "point": point,
            "point_label": mapidea.point_label,
        }
    )

    return data

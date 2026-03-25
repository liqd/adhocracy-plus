from django import template

register = template.Library()

@register.inclusion_tag('a4_candy_contrib/includes/pagination.html', takes_context=True)
def pagination(context, page_obj, param_name='page'):
    """
    Berlin Design System pagination.
    Shows all pages if total <= 6, otherwise shows first, last, current with neighbors, and ellipsis.
    
    Usage:
        {% pagination page_obj %}
        {% pagination page_obj param_name='p' %}
    """
    request = context.get('request')
    current = page_obj.number
    total = page_obj.paginator.num_pages

    if total <= 1:
        return {'show_pagination': False}

    # Build list of page numbers/ellipsis to display
    pages = []
    if total <= 6:
        # Show all pages
        pages = list(range(1, total + 1))
    else:
        # Always show first page
        pages.append(1)

        # Calculate range around current page
        left = max(2, current - 1)
        right = min(total - 1, current + 1)

        # Add left ellipsis if needed (current page is beyond page 3)
        if left > 2:
            pages.append('...')

        # Add pages around current
        for i in range(left, right + 1):
            if i not in pages:
                pages.append(i)

        # Add right ellipsis if needed (current page is before last 2 pages)
        if right < total - 1:
            pages.append('...')

        # Always show last page
        pages.append(total)

    # URL builder preserving GET parameters
    def get_page_url(page_num):
        params = request.GET.copy()
        params[param_name] = page_num
        return f"?{params.urlencode()}#index"

    # Determine if previous/next should be disabled
    has_previous = page_obj.has_previous()
    has_next = page_obj.has_next()

    return {
        'show_pagination': True,
        'pages': pages,
        'current': current,
        'total': total,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_url': get_page_url(current - 1) if has_previous else '#',
        'next_url': get_page_url(current + 1) if has_next else '#',
        'get_page_url': get_page_url,
        'param_name': param_name,
    }
from django import template
from urllib.parse import urlencode

register = template.Library()

@register.inclusion_tag('a4_candy_contrib/includes/pagination.html', takes_context=True)
def pagination(context, page_obj, param_name='page'):
    """
    Berlin Design System pagination.
    Shows all pages if total <= 6, otherwise shows first, last, current with neighbors, and ellipsis.
    Only shows ellipsis when there are at least 2 pages hidden between sections.
    
    Usage:
        {% pagination page_obj %}
        {% pagination page_obj param_name='p' %}
    """
    request = context.get('request')
    current = page_obj.number
    total = page_obj.paginator.num_pages

    if total <= 1:
        return {'show_pagination': False}

    pages = []
    
    # Show all pages if total is 6 or less
    if total <= 6:
        pages = list(range(1, total + 1))
    else:
        # Always show first page
        pages.append(1)
        
        # Determine pages around current (show 1 on each side)
        left_page = current - 1
        right_page = current + 1
        
        # Handle left side
        if left_page > 2:
            # If there are 2 or more pages hidden between 1 and left_page, show ellipsis
            if left_page > 3:
                pages.append('...')
            else:
                # Only page 2 is hidden, show it
                pages.append(2)
        elif left_page == 2:
            pages.append(2)
        
        # Add left neighbor if it exists and not already added
        if left_page > 1 and left_page not in pages:
            pages.append(left_page)
        
        # Add current page
        pages.append(current)
        
        # Add right neighbor if it exists
        if right_page < total and right_page not in pages:
            pages.append(right_page)
        
        # Handle right side
        if right_page < total - 1:
            # If there are 2 or more pages hidden between right_page and last, show ellipsis
            if right_page < total - 2:
                pages.append('...')
            else:
                # Only the page before last is hidden, show it
                if total - 1 not in pages:
                    pages.append(total - 1)
        
        # Always show last page
        if total not in pages:
            pages.append(total)
    
    # URL builder that preserves ALL GET parameters
    def get_page_url(page_num):
        params = request.GET.copy()
        params[param_name] = page_num
        return f"?{params.urlencode()}#index"
    
    has_previous = page_obj.has_previous()
    has_next = page_obj.has_next()
    
    previous_url = get_page_url(current - 1) if has_previous else '#'
    next_url = get_page_url(current + 1) if has_next else '#'

    return {
        'show_pagination': True,
        'pages': pages,
        'current': current,
        'total': total,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_url': previous_url,
        'next_url': next_url,
        'param_name': param_name,
    }
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)


def _build_page_list(current, total):
    """Build the list of pages to display with ellipsis logic."""
    pages = []
    
    if total <= 6:
        pages = list(range(1, total + 1))
    else:
        pages.append(1)
        
        left_page = current - 1
        right_page = current + 1
        
        # Handle left side
        if left_page > 2:
            if left_page > 3:
                pages.append('...')
            else:
                if 2 not in pages:
                    pages.append(2)
        elif left_page == 2:
            if 2 not in pages:
                pages.append(2)
        
        # Add left neighbor
        if left_page > 1 and left_page not in pages:
            pages.append(left_page)
        
        # Add current page
        if current not in pages:
            pages.append(current)
        
        # Add right neighbor
        if right_page < total and right_page not in pages:
            pages.append(right_page)
        
        # Handle right side
        if right_page < total - 1:
            if right_page < total - 2:
                pages.append('...')
            else:
                if total - 1 not in pages:
                    pages.append(total - 1)
        
        # Always show last page
        if total not in pages:
            pages.append(total)
    
    return pages


@register.inclusion_tag('a4_candy_contrib/includes/pagination.html', takes_context=True)
def pagination(context, page_obj, param_name='page'):
    """
    Pagination for regular (non-HTMX) requests.
    
    Usage:
        {% pagination page_obj %}
        {% pagination page_obj param_name='p' %}
    """
    request = context.get('request')
    current = page_obj.number
    total = page_obj.paginator.num_pages

    if total <= 1:
        return {'show_pagination': False}

    pages = _build_page_list(current, total)
    
    has_previous = page_obj.has_previous()
    has_next = page_obj.has_next()
    
    # Build URLs for each page
    page_urls = {}
    for page in pages:
        if page != '...':
            params = request.GET.copy()
            params[param_name] = page
            page_urls[page] = f"?{params.urlencode()}#index"
    
    # Previous/Next URLs
    previous_url = '#'
    next_url = '#'
    
    if has_previous:
        params = request.GET.copy()
        params[param_name] = current - 1
        previous_url = f"?{params.urlencode()}#index"
    
    if has_next:
        params = request.GET.copy()
        params[param_name] = current + 1
        next_url = f"?{params.urlencode()}#index"
    
    return {
        'show_pagination': True,
        'is_htmx': False,
        'pages': pages,
        'current': current,
        'total': total,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_url': previous_url,
        'next_url': next_url,
        'page_urls': page_urls,
        'param_name': param_name,
    }


@register.inclusion_tag('a4_candy_contrib/includes/pagination.html', takes_context=True)
def htmx_pagination(context, page_obj, param_name='page', hx_target=None, hx_get_url=None, section_id=None):
    """
    Pagination for HTMX requests.
    
    Usage:
        {% htmx_pagination page_obj hx_target="section-id" hx_get_url="{% url 'partial-url' %}" %}
        Pass the section_id (without #) and the tag will add the # prefix.
    """
    request = context.get('request')
    current = page_obj.number
    total = page_obj.paginator.num_pages

    if total <= 1:
        return {'show_pagination': False}

    pages = _build_page_list(current, total)
    
    has_previous = page_obj.has_previous()
    has_next = page_obj.has_next()
    
    # Add # prefix to hx_target if it's not already there
    if hx_target and not hx_target.startswith('#'):
        hx_target = f"#{hx_target}"
    
    # Build URLs for each page
    page_urls = {}
    page_htmx_urls = {}
    
    for page in pages:
        if page != '...':
            # Regular URL
            params = request.GET.copy()
            params[param_name] = page
            page_urls[page] = f"?{params.urlencode()}#index"
            
            # HTMX URL
            if hx_get_url:
                page_htmx_urls[page] = f"{hx_get_url}?{params.urlencode()}"
            else:
                page_htmx_urls[page] = page_urls[page]
    
    # Previous/Next URLs
    previous_url = '#'
    next_url = '#'
    previous_htmx_url = '#'
    next_htmx_url = '#'
    
    if has_previous:
        params = request.GET.copy()
        params[param_name] = current - 1
        previous_url = f"?{params.urlencode()}#index"
        if hx_get_url:
            previous_htmx_url = f"{hx_get_url}?{params.urlencode()}"
        else:
            previous_htmx_url = previous_url
    
    if has_next:
        params = request.GET.copy()
        params[param_name] = current + 1
        next_url = f"?{params.urlencode()}#index"
        if hx_get_url:
            next_htmx_url = f"{hx_get_url}?{params.urlencode()}"
        else:
            next_htmx_url = next_url
    
    return {
        'show_pagination': True,
        'is_htmx': True,
        'pages': pages,
        'current': current,
        'total': total,
        'has_previous': has_previous,
        'has_next': has_next,
        'previous_url': previous_url,
        'next_url': next_url,
        'previous_htmx_url': previous_htmx_url,
        'next_htmx_url': next_htmx_url,
        'page_urls': page_urls,
        'page_htmx_urls': page_htmx_urls,
        'param_name': param_name,
        'hx_target': hx_target,
        'section_id': section_id,
    }
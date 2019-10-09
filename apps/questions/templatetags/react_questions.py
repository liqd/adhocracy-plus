import json

from django import template
from django.urls import reverse
from django.utils.html import format_html

from adhocracy4.rules.discovery import NormalUser

register = template.Library()


@register.simple_tag(takes_context=True)
def react_questions(context, obj):
    request = context['request']

    user = request.user
    is_moderator = user.has_perm('a4_candy_questions.moderate_questions', obj)
    categories = [category.name for category in obj.category_set.all()]
    questions_api_url = reverse('questions-list', kwargs={'module_pk': obj.pk})

    permission = 'a4_candy_likes.add_like_model'
    has_liking_permission = user.has_perm(
        permission, obj)
    would_have_liking_permission = NormalUser().would_have_perm(
        permission, obj
    )

    attributes = {
        'questions_api_url': questions_api_url,
        'isModerator': is_moderator,
        'categories': categories,
        'hasLikingPermission': (has_liking_permission
                                or would_have_liking_permission)
    }

    return format_html(
        '<div data-speakup-widget="questions" '
        'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes)
    )


@register.simple_tag(takes_context=True)
def react_questions_statistics(context, obj):
    request = context['request']

    categories = [category.name for category in obj.category_set.all()]
    questions_api_url = reverse('questions-list', kwargs={'module_pk': obj.pk})
    user = request.user
    is_moderator = user.has_perm('a4_candy_questions.moderate_questions', obj)

    attributes = {
        'questions_api_url': questions_api_url,
        'categories': categories,
        'isModerator': is_moderator,
    }

    return format_html(
        '<div data-speakup-widget="statistics" '
        'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes)
    )


@register.simple_tag(takes_context=True)
def react_questions_present(context, obj):

    categories = [category.name for category in obj.category_set.all()]
    questions_api_url = reverse('questions-list', kwargs={'module_pk': obj.pk})
    request = context['request']
    url = obj.project.get_absolute_url()
    full_url = request.build_absolute_uri(url)

    attributes = {
        'questions_api_url': questions_api_url,
        'categories': categories,
        'url': full_url,
        'title': obj.project.name
    }

    return format_html(
        '<div data-speakup-widget="present" '
        'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes)
    )

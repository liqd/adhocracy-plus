import json

from django import template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from adhocracy4.rules.discovery import NormalUser
from apps.cms.settings.helpers import get_important_page_url

register = template.Library()


@register.simple_tag(takes_context=True)
def react_interactiveevents(context, obj):
    request = context['request']

    user = request.user
    is_moderator = \
        user.has_perm('a4_candy_interactive_events.moderate_livequestions',
                      obj)
    categories = [category.name for category in obj.category_set.all()]
    category_dict = {category.pk: category.name
                     for category in obj.category_set.all()}
    questions_api_url = reverse('interactiveevents-list',
                                kwargs={'module_pk': obj.pk})

    private_policy_label = str(_('I confirm that I have read and accepted the '
                                 '{}terms of use{} and the {}data protection '
                                 'policy{}.'))

    terms_of_use_url = get_important_page_url('terms_of_use')
    data_protection_policy_url = \
        get_important_page_url('data_protection_policy')

    likes_api_url = '/api/livequestions/LIVEQUESTIONID/likes/'
    present_url = \
        reverse('question-present',
                kwargs={'module_slug': obj.slug,
                        'organisation_slug': obj.project.organisation.slug})

    like_permission = 'a4_candy_interactive_events.add_like_model'
    has_liking_permission = user.has_perm(
        like_permission, obj)
    would_have_liking_permission = NormalUser().would_have_perm(
        like_permission, obj
    )

    ask_permissions = 'a4_candy_interactive_events.add_livequestion'
    has_ask_questions_permissions = user.has_perm(ask_permissions, obj)
    would_have_ask_questions_permission = NormalUser().would_have_perm(
        ask_permissions, obj)

    attributes = {
        'information': obj.description,
        'questions_api_url': questions_api_url,
        'likes_api_url': likes_api_url,
        'present_url': present_url,
        'isModerator': is_moderator,
        'categories': categories,
        'category_dict': category_dict,
        'hasLikingPermission': (has_liking_permission
                                or would_have_liking_permission),
        'hasAskQuestionsPermission': (has_ask_questions_permissions
                                      or would_have_ask_questions_permission),
        'privatePolicyLabel': private_policy_label,
        'termsOfUseUrl': terms_of_use_url,
        'dataProtectionPolicyUrl': data_protection_policy_url
    }

    return format_html(
        '<div data-aplus-widget="questions" '
        'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes)
    )


@register.simple_tag(takes_context=True)
def react_interactiveevents_present(context, obj):

    categories = [category.name for category in obj.category_set.all()]
    questions_api_url = reverse('interactiveevents-list',
                                kwargs={'module_pk': obj.pk})
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
        '<div data-aplus-widget="present" '
        'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes)
    )

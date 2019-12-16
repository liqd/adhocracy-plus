import pytest
import rules

from adhocracy4.test import helpers


@pytest.mark.django_db
def test_get_change_perm(rf, subject_factory):
    obj = subject_factory()
    request = rf.get('/')
    template = ('{% load item_tags %}'
                '{% get_item_view_permission obj as view_perm %}'
                '{% get_item_add_permission obj as add_perm %}'
                '{% get_item_change_permission obj as change_perm %}'
                '{% get_item_delete_permission obj as delete_perm %}'
                '{{ view_perm }}'
                '{{ add_perm }}'
                '{{ change_perm }}'
                '{{ delete_perm }}')
    context = {'request': request, 'obj': obj}
    helpers.render_template(template, context)

    assert 'a4_candy_debate.view_subject' == context['view_perm']
    assert rules.perm_exists(context['view_perm'])
    assert 'a4_candy_debate.add_subject' == context['add_perm']
    assert rules.perm_exists(context['add_perm'])
    assert 'a4_candy_debate.change_subject' == context['change_perm']
    assert rules.perm_exists(context['change_perm'])
    assert 'a4_candy_debate.delete_subject' == context['delete_perm']

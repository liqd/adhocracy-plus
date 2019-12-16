import rules

from adhocracy4.modules import predicates as module_predicates

rules.add_perm(
    'a4_candy_debate.add_subject',
    module_predicates.is_project_admin
)

rules.add_perm(
    'a4_candy_debate.change_subject',
    module_predicates.is_project_admin
)

rules.add_perm(
    'a4_candy_debate.view_subject',
    (module_predicates.is_project_admin |
     module_predicates.is_allowed_view_item)
)

rules.add_perm(
    'a4_candy_debate.comment_subject',
    module_predicates.is_allowed_comment_item
)

import rules

from adhocracy4.modules import predicates as module_predicates

rules.add_perm(
    'a4_candy_activities.change_activity',
    module_predicates.is_project_admin
)

rules.add_perm(
    'a4_candy_activities.view_activity',
    module_predicates.is_allowed_view_item
)

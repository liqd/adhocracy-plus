import rules

from adhocracy4.modules import predicates as module_predicates

rules.add_perm(
    "a4_candy_customfields.change_customfieldsettings",
    module_predicates.is_allowed_crud_project,
)

rules.add_perm(
    "a4_candy_customfields.view_customfieldsettings",
    module_predicates.is_allowed_moderate_project,
)

import rules

from adhocracy4.modules import predicates as module_predicates

rules.add_perm(
    "a4_candy_moderatorfeedback.add_moderatorcommentfeedback",
    module_predicates.is_allowed_moderate_project,
)

rules.add_perm(
    "a4_candy_moderatorfeedback.change_moderatorcommentfeedback",
    module_predicates.is_allowed_moderate_project,
)

rules.add_perm(
    "a4_candy_moderatorfeedback.delete_moderatorcommentfeedback",
    module_predicates.is_allowed_moderate_project,
)

rules.add_perm(
    "a4_candy_moderatorfeedback.view_moderatorcommentfeedback",
    module_predicates.is_allowed_moderate_project
    | module_predicates.is_public_context
    | module_predicates.is_context_member,
)

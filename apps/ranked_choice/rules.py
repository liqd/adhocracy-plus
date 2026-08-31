import rules

from adhocracy4.modules import predicates as module_predicates
from adhocracy4.phases import predicates as phase_predicates

from apps.ideas.models import Idea


@rules.predicate
def is_allowed_rank(user, module):
    """Return if the user is allowed to cast a ranked ballot in a module.

    Mirrors ``adhocracy4.modules.predicates.is_allowed_rate_item`` but gates
    on the ``rank`` feature of the currently active phase instead of ``rate``.
    The permission object is the module.
    """
    if module:
        return module_predicates.is_allowed_moderate_project(user, module) | (
            module_predicates.is_context_member(user, module)
            & module_predicates.is_live_context(user, module)
            & phase_predicates.has_feature_active(module, Idea, "rank")
        )
    return False


rules.add_perm("a4_candy_ranked_choice.rank_idea", is_allowed_rank)
rules.add_perm(
    "a4_candy_ranked_choice.moderate_ranked_choice",
    module_predicates.is_allowed_moderate_project,
)
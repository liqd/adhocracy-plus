import rules

from adhocracy4.modules import predicates as module_predicates
from apps.contrib import predicates as contrib_predicates

from . import models

rules.add_perm(
    'liqd_product_polls.change_poll',
    module_predicates.is_context_initiator |
    module_predicates.is_context_moderator
)

rules.add_perm(
    'liqd_product_polls.view_poll',
    (module_predicates.is_project_admin |
     (module_predicates.is_allowed_view_item &
      contrib_predicates.has_context_started))
)

rules.add_perm(
    'liqd_product_polls.comment_poll',
    module_predicates.is_allowed_comment_item
)


# It has to be ensured that the permission is always checked against a module
# never a Vote object.
rules.add_perm(
    'liqd_product_polls.add_vote',
    module_predicates.is_allowed_add_item(models.Vote)
)

import rules
from rules.predicates import is_superuser

from adhocracy4.comments.rules import content_object_allows_comment
from adhocracy4.modules import predicates as module_predicates

rules.set_perm(
    "a4comments.change_comment",
    is_superuser
    | (
        module_predicates.is_context_member
        & content_object_allows_comment
        & module_predicates.is_owner
    ),
)

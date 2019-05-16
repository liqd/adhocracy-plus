import rules

from adhocracy4.modules import predicates as module_predicates
from liqd_product.apps.contrib import predicates as contrib_predicates

rules.add_perm(
    'liqd_product_documents.view_chapter',
    (module_predicates.is_project_admin |
     (module_predicates.is_allowed_view_item &
      contrib_predicates.has_context_started))
)

rules.add_perm(
    'liqd_product_documents.view_paragraph',
    (module_predicates.is_project_admin |
     (module_predicates.is_allowed_view_item &
      contrib_predicates.has_context_started))
)

rules.add_perm(
    'liqd_product_documents.add_chapter',
    module_predicates.is_project_admin
)

rules.add_perm(
    'liqd_product_documents.change_chapter',
    module_predicates.is_project_admin
)

rules.add_perm(
    'liqd_product_documents.comment_paragraph',
    module_predicates.is_allowed_comment_item
)

rules.add_perm(
    'liqd_product_documents.comment_chapter',
    module_predicates.is_allowed_comment_item
)

import rules
from rules.predicates import is_superuser

from .predicates import is_partner_admin

rules.add_perm('liqd_product_partners.change_partner',
               is_superuser | is_partner_admin)

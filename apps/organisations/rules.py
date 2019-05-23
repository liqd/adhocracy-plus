import rules
from rules.predicates import is_superuser

from .predicates import is_initiator

# FIXME: Customers/Muncipials containing the org will be allowed, too
rules.add_perm('a4_candy_organisations.change_organisation',
               is_superuser | is_initiator)

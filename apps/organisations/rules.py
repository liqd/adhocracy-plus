import rules
from rules.predicates import is_superuser

from adhocracy4.organisations.predicates import is_initiator

rules.add_perm('a4_candy_organisations.change_organisation',
               is_superuser | is_initiator)

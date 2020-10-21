import rules
from rules.predicates import is_superuser

from adhocracy4.organisations.predicates import is_initiator
from adhocracy4.organisations.predicates import is_org_member
from adhocracy4.projects.predicates import is_live
from adhocracy4.projects.predicates import is_moderator
from adhocracy4.projects.predicates import is_project_member
from adhocracy4.projects.predicates import is_public
from adhocracy4.projects.predicates import is_semipublic

rules.add_perm('a4_candy_projects.change_project',
               is_superuser | is_initiator)

rules.add_perm('a4_candy_projects.view_project',
               is_superuser | is_initiator | is_moderator |
               ((is_public | is_semipublic | is_org_member | is_project_member) & is_live))

rules.add_perm('a4_candy_projects.delete_project',
               is_superuser | is_initiator)

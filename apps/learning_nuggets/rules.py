import rules
from rules.predicates import always_true

from adhocracy4.organisations.predicates import is_initiator
from adhocracy4.projects.predicates import is_moderator

rules.add_perm("a4_candy_learning_nuggets.view_moderator_content", is_moderator)

rules.add_perm("a4_candy_learning_nuggets.view_initiator_content", is_initiator)

rules.add_perm("a4_candy_learning_nuggets.view_participant_content", always_true)

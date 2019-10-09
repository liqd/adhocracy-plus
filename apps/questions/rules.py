import rules
from rules.predicates import is_superuser

from adhocracy4.modules.predicates import is_context_initiator
from adhocracy4.modules.predicates import is_context_moderator
from adhocracy4.phases.predicates import phase_allows_add

from .models import Question

rules.add_perm('a4_candy_questions.change_question',
               is_superuser | is_context_moderator | is_context_initiator)


rules.add_perm('a4_candy_questions.propose_question',
               phase_allows_add(Question))


rules.add_perm('a4_candy_questions.view_question', rules.always_allow)


rules.add_perm('a4_candy_questions.moderate_questions',
               is_superuser | is_context_moderator | is_context_initiator)

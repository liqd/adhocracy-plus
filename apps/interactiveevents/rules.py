import rules

from adhocracy4.modules.predicates import is_allowed_moderate_project
from adhocracy4.phases.predicates import phase_allows_add

from .models import LiveQuestion
from .predicates import phase_allows_like
from .predicates import phase_allows_like_model

rules.add_perm(
    "a4_candy_interactive_events.change_livequestion", is_allowed_moderate_project
)


rules.add_perm(
    "a4_candy_interactive_events.add_livequestion", phase_allows_add(LiveQuestion)
)


rules.add_perm("a4_candy_interactive_events.view_livequestion", rules.always_allow)


rules.add_perm(
    "a4_candy_interactive_events.moderate_livequestions", is_allowed_moderate_project
)


rules.add_perm("a4_candy_interactive_events.add_like", phase_allows_like)


rules.add_perm(
    "a4_candy_interactive_events.add_like_model", phase_allows_like_model(LiveQuestion)
)

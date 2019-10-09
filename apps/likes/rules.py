import rules

from apps.questions.models import Question

from .predicates import phase_allows_like
from .predicates import phase_allows_like_model

rules.add_perm('a4_candy_likes.add_like', phase_allows_like)

rules.add_perm('a4_candy_likes.add_like_model',
               phase_allows_like_model(Question))

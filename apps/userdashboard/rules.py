import rules

from adhocracy4.modules.predicates import is_allowed_moderate_project
from apps.users.predicates import is_moderator

rules.add_perm('a4_candy_userdashboard.view_moderation_dashboard',
               is_moderator)

rules.add_perm('a4_candy_userdashboard.view_moderation_comment',
               is_allowed_moderate_project)

rules.add_perm('a4_candy_userdashboard.change_moderation_comment',
               is_allowed_moderate_project)

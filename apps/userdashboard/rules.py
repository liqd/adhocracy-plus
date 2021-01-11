import rules

from apps.users.predicates import is_moderator

rules.add_perm('a4_candy_userdashboard.view_moderation_dashboard',
               is_moderator)

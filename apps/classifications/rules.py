import rules

from adhocracy4.projects.predicates import is_moderator as is_project_moderator

rules.add_perm('a4_candy_classifications.view_userclassification',
               is_project_moderator)

rules.add_perm('a4_candy_classifications.view_aiclassification',
               is_project_moderator)

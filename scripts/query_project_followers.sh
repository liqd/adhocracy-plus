#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
PROJECT_ID="${1:-3}"

venv/bin/python manage.py shell -c "
from adhocracy4.follows.models import Follow
from adhocracy4.projects.models import Project
from guest_user.functions import get_guest_model, is_guest_user

project = Project.objects.get(pk=${PROJECT_ID})
guest_user_ids = set(get_guest_model().objects.values_list('user_id', flat=True))
follows = (
    Follow.objects.filter(project=project, enabled=True)
    .select_related('creator')
    .order_by('-created')
)

print('Project:', project.pk, '-', project.name)
print('Enabled follows (all):', follows.count())
print('Registered only (UI):', follows.exclude(creator_id__in=guest_user_ids).count())
print()

for follow in follows:
    user = follow.creator
    guest = is_guest_user(user)
    ui = 'hidden (guest)' if guest else 'shown'
    print(
        '- follow_id=%s user_id=%s username=%s guest=%s ui=%s'
        % (follow.pk, user.pk, repr(user.username), guest, ui)
    )

if not follows.exists():
    print('(no enabled follows)')
"

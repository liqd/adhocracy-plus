from pytest_factoryboy import register

from adhocracy4.test.factories import polls as poll_factories

from . import factories as invites

register(invites.ModeratorInviteFactory)
register(invites.ParticipantInviteFactory)
register(poll_factories.PollFactory)

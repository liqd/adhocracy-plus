from pytest_factoryboy import register

from adhocracy4.test.factories import FollowFactory

from . import factories

register(FollowFactory)
register(factories.NewsletterFactory)
register(factories.EmailAddressFactory)

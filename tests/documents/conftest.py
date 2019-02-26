from pytest_factoryboy import register

from . import factories as document_factories

register(document_factories.ChapterFactory)
register(document_factories.ParagraphFactory)

from django.utils import translation
from wagtail.core.blocks.stream_block import StreamValue


class TranslatedField(object):

    def __init__(self, de_field, en_field):
        self.de_field = de_field
        self.en_field = en_field

    def hasContent(self, field):
        if isinstance(field, StreamValue):
            value = field.stream_data
            if value:
                return True
            else:
                return False
        elif isinstance(field, str):
            if field:
                return True
            else:
                return False
        else:
            return False

    def __get__(self, instance, owner):
        de = getattr(instance, self.de_field)
        en = getattr(instance, self.en_field)

        if translation.get_language() == 'en' and self.hasContent(en):
            return en
        else:
            return de


class TranslatedFieldLegal(object):

    def __init__(self, de_field, en_field, nl_field, ky_field, ru_field):
        self.de_field = de_field
        self.en_field = en_field
        self.nl_field = nl_field
        self.ky_field = ky_field
        self.ru_field = ru_field

    def hasContent(self, field):
        if isinstance(field, StreamValue):
            value = field.stream_data
            if value:
                return True
            else:
                return False
        elif isinstance(field, str):
            if field:
                return True
            else:
                return False
        else:
            return False

    def __get__(self, instance, owner):
        de = getattr(instance, self.de_field)
        en = getattr(instance, self.en_field)
        nl = getattr(instance, self.nl_field)
        ky = getattr(instance, self.ky_field)
        ru = getattr(instance, self.ru_field)

        if translation.get_language() == 'en' and self.hasContent(en):
            return en
        elif translation.get_language() == 'nl' and self.hasContent(nl):
            return nl
        elif translation.get_language() == 'ky' and self.hasContent(ky):
            return ky
        elif translation.get_language() == 'ru' and self.hasContent(ru):
            return ru
        else:
            return de

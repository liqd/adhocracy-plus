from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core import validators
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from adhocracy4.images.fields import ConfiguredImageField

from . import USERNAME_INVALID_MESSAGE
from . import USERNAME_REGEX


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=60,
        unique=True,
        help_text=_(
            'Required. 60 characters or fewer. Letters, digits, spaces and '
            '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                USERNAME_REGEX, USERNAME_INVALID_MESSAGE, 'invalid')],
        error_messages={
            'unique': _('A user with that username already exists.'),
            'used_as_email': _('This username is already used as an '
                               'e-mail address.')}
    )

    email = models.EmailField(
        _('Email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email address already exists.')}
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.')
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.')
    )

    date_joined = models.DateTimeField(
        editable=False,
        default=timezone.now
    )

    get_notifications = models.BooleanField(
        verbose_name=_('Send me email notifications'),
        default=True,
        help_text=_(
            'Designates whether you want to receive notifications. '
            'Unselect if you do not want to receive notifications.')
    )

    get_newsletters = models.BooleanField(
        verbose_name=_('I would like to receive further information'),
        default=False,
        help_text=_(
            'Projects you are following can send you '
            'additional information via email.')
    )

    bio = models.TextField(
        blank=True,
        max_length=255,
        verbose_name=_('Biography'),
        help_text=_(
            'Tell us about yourself in 255 characters!')
    )

    twitter_handle = models.CharField(
        blank=True,
        max_length=15,
        verbose_name=_('Twitter handle'),
    )

    facebook_handle = models.CharField(
        blank=True,
        max_length=50,
        verbose_name=_('Facebook name'),
        help_text=_(
            'Your facebook name is the last part of the URL, '
            'when you access your profile.')
    )

    homepage = models.URLField(
        blank=True,
        max_length=50,
        verbose_name=_('Homepage'),
    )

    _avatar = ConfiguredImageField(
        'avatar',
        upload_to='users/images',
        blank=True,
        verbose_name=_('Avatar picture'),
    )

    language = models.CharField(
        verbose_name=_('Your preferred language'),
        choices=settings.LANGUAGES,
        default=settings.DEFAULT_USER_LANGUAGE_CODE,
        max_length=4,
        help_text=_(
            'Specify your preferred language for the user interface '
            'and the notifications of the platform.'),
    )

    objects = auth_models.UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @cached_property
    def organisations(self):
        return self.organisation_set.all()

    @cached_property
    def avatar(self):
        if self._avatar:
            return self._avatar

    @cached_property
    def avatar_fallback(self):
        number = self.pk % 5
        return static('images/avatar-{0:02d}.svg'.format(number))

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        full_name = '%s <%s>' % (self.username, self.email)
        return full_name.strip()

    def get_absolute_url(self):
        return reverse('profile', args=[str(self.username)])

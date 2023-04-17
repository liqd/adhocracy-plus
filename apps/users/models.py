from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core import validators
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from adhocracy4.images.fields import ConfiguredImageField
from adhocracy4.projects.enums import Access
from adhocracy4.projects.models import Project
from apps.organisations.models import OrganisationTermsOfUse

from . import USERNAME_INVALID_MESSAGE
from . import USERNAME_REGEX


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    username = models.CharField(
        _("username"),
        max_length=60,
        unique=True,
        help_text=_(
            "Required. 60 characters or fewer. Letters, digits, spaces and "
            "@/./+/-/_ only."
        ),
        validators=[
            validators.RegexValidator(
                USERNAME_REGEX, USERNAME_INVALID_MESSAGE, "invalid"
            )
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
            "used_as_email": _("This username is invalid."),
        },
    )

    email = models.EmailField(
        _("Email address"),
        unique=True,
        error_messages={"unique": _("Email is invalid or already taken.")},
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    date_joined = models.DateTimeField(editable=False, default=timezone.now)

    get_notifications = models.BooleanField(
        verbose_name=_("Send me email notifications"),
        default=True,
        help_text=_(
            "Designates whether you want to receive notifications. "
            "Unselect if you do not want to receive notifications."
        ),
    )

    get_newsletters = models.BooleanField(
        verbose_name=_("I would like to receive further information"),
        default=False,
        help_text=_(
            "Projects you are following can send you "
            "additional information via email."
        ),
    )

    bio = models.TextField(
        blank=True,
        max_length=255,
        verbose_name=_("Biography"),
        help_text=_("Tell us about yourself in 255 characters!"),
    )

    twitter_handle = models.CharField(
        blank=True,
        max_length=15,
        verbose_name=_("Twitter handle"),
    )

    facebook_handle = models.CharField(
        blank=True,
        max_length=50,
        verbose_name=_("Facebook name"),
        help_text=_(
            "Your facebook name is the last part of the URL, "
            "when you access your profile."
        ),
    )

    homepage = models.URLField(
        blank=True,
        max_length=50,
        verbose_name=_("Homepage"),
    )

    _avatar = ConfiguredImageField(
        "avatar",
        upload_to="users/images",
        blank=True,
        verbose_name=_("Avatar picture"),
    )

    language = models.CharField(
        verbose_name=_("Your preferred language"),
        choices=settings.LANGUAGES,
        default=settings.DEFAULT_USER_LANGUAGE_CODE,
        max_length=4,
        help_text=_(
            "Specify your preferred language for the user interface "
            "and the notifications of the platform."
        ),
    )

    objects = auth_models.UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_projects_follow_list(self, exclude_private_projects=False):
        projects = Project.objects.filter(
            follow__creator=self, follow__enabled=True, is_draft=False
        ).select_related("organisation")
        if exclude_private_projects:
            projects = projects.exclude(models.Q(access=Access.PRIVATE))

        now = timezone.now()

        sorted_active_projects = (
            projects.annotate(project_start=models.Min("module__phase__start_date"))
            .annotate(project_end=models.Max("module__phase__end_date"))
            .filter(project_start__lte=now, project_end__gt=now)
            .order_by("project_end")
        )

        sorted_future_projects = (
            projects.annotate(project_start=models.Min("module__phase__start_date"))
            .filter(models.Q(project_start__gt=now) | models.Q(project_start=None))
            .order_by("project_start")
        )

        sorted_past_projects = (
            projects.annotate(project_start=models.Min("module__phase__start_date"))
            .annotate(project_end=models.Max("module__phase__end_date"))
            .filter(project_end__lt=now)
            .order_by("project_start")
        )

        return sorted_active_projects, sorted_future_projects, sorted_past_projects

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
        return static("images/avatar-{0:02d}.svg".format(number))

    @cached_property
    def avatar_fallback_png(self):
        number = self.pk % 5
        return static("images/avatar-{0:02d}.png".format(number))

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        full_name = "%s <%s>" % (self.username, self.email)
        return full_name.strip()

    def get_absolute_url(self):
        return reverse("profile", args=[str(self.username)])

    def has_agreed_on_org_terms(self, organisation):
        return OrganisationTermsOfUse.objects.filter(
            user=self, organisation=organisation, has_agreed=True
        ).exists()

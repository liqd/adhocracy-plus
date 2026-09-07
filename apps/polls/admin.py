from django import forms
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext_lazy as _

from adhocracy4.polls.models import Answer
from adhocracy4.projects.admin import ProjectAdminFilter


class AnswerForm(forms.ModelForm):
    """ModelForm that keeps the original (pre-submit) field values around so the
    change message can record both old and new values."""

    class Meta:
        model = Answer
        fields = ["answer"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_values = {
            name: getattr(self.instance, name, None) for name in self.fields
        }


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag")
    list_filter = ("action_flag", "user", "content_type", "action_time")
    date_hierarchy = "action_time"
    search_fields = ("object_repr", "change_message", "user__username", "user__email")
    readonly_fields = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AnswerProjectFilter(ProjectAdminFilter):
    project_key = "question__poll__module__project"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    form = AnswerForm
    list_display = (
        "answer_preview",
        "question",
        "poll",
        "creator",
        "created",
    )
    list_filter = (
        "question__poll__module__project__organisation",
        "question__poll__module__project__is_archived",
        AnswerProjectFilter,
        "question",
    )
    date_hierarchy = "created"
    search_fields = (
        "answer",
        "creator__username",
        "creator__email",
        "question__poll__module__project__name",
    )
    readonly_fields = (
        "question",
        "creator",
        "content_id",
        "created",
        "modified",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "question",
                    "answer",
                    "creator",
                    "content_id",
                    "created",
                    "modified",
                )
            },
        ),
    )

    @admin.display(description=_("Answer"), ordering="answer")
    def answer_preview(self, obj):
        """Short preview of the answer text."""
        return obj.answer[:50]

    @admin.display(description=_("Poll"), ordering="question__poll")
    def poll(self, obj):
        return obj.question.poll

    def construct_change_message(self, request, form, formsets, add=False):
        if add or not form.changed_data:
            return super().construct_change_message(request, form, formsets, add)
        original = getattr(form, "original_values", {})
        parts = []
        for field in form.changed_data:
            label = form.fields[field].label or field
            old = original.get(field, "")
            new = form.cleaned_data.get(field, "")
            parts.append(
                _("Changed {label}: “{old}” → “{new}”.").format(
                    label=label, old=old, new=new
                )
            )
        return " ".join(parts)

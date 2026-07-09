from django.contrib import admin

from . import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient",
        "notification_type",
        "read",
        "created",
        "read_at",
    )
    list_filter = ("notification_type", "read", "created")
    search_fields = ("recipient__username", "recipient__email", "message_template")
    date_hierarchy = "created"
    raw_id_fields = ("recipient",)
    readonly_fields = ("created", "read_at")
    ordering = ("-created",)

    fieldsets = (
        (None, {"fields": ("recipient", "notification_type")}),
        ("Content", {"fields": ("message_template", "context")}),
        ("Status", {"fields": ("read", "read_at", "created")}),
        ("Links", {"fields": ("target_url",)}),
    )


@admin.register(models.NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "email_moderation", "notify_moderation")
    list_filter = (
        "email_newsletter",
        "email_initiator_publish_results",
        "email_project_updates",
        "notify_project_updates",
        "email_project_events",
        "notify_project_events",
        "email_user_engagement",
        "notify_user_engagement",
        "email_invitations",
        "notify_invitations",
        "email_moderation",
        "notify_moderation",
    )
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)

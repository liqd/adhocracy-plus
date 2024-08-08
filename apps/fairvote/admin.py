from django.contrib import admin

from . import models
from .algorithms import accept_idea
from .algorithms import update_idea_choins
from .forms import UpdateChoinsForm
from .views import ChoinView


@admin.register(models.Choin)
class ChoinAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "choins")
    action_form = UpdateChoinsForm
    actions = ["update_user_choins", "add_all_users_choins"]

    def update_user_choins(self, request, queryset):
        """
        Add or change the number of choins in a user's wallet
        """
        choins_amount = request.POST["choins_amount"]
        append = request.POST.get("append", None)
        for user_choins in queryset:
            user_choins.update_user_choins(choins_amount, append)

    update_user_choins.short_description = "Update Choins for Selected users choins"

    def add_all_users_choins(self, request, queryset):
        ChoinView.create_users_choins()
        self.message_user(
            request, f"create or update {queryset.count()} users choins."
        )  # Display a success message

    add_all_users_choins.short_description = "Add users choins"


@admin.register(models.IdeaChoin)
class IdeaChoinAdmin(admin.ModelAdmin):
    list_display = ("idea", "choins", "order")
    ordering = ["-choins"]
    actions = [
        "update_ideas_choins",
        "add_all_ideas_choins",
        "accept_selected_idea",
        "increase_choins_to_accept_idea",
    ]

    def update_ideas_choins(self, request, queryset):
        for idea_choins in queryset:
            update_idea_choins(idea_choins)
        self.message_user(request, f"Updated {queryset.count()} ideas choins.")

    update_ideas_choins.short_description = "Update selected ideas choins"

    def add_all_ideas_choins(self, request, queryset):
        ChoinView.create_ideas_choins()
        self.message_user(
            request, f"create or update {queryset.count()} ideas choins."
        )  # Display a success message

    add_all_ideas_choins.short_description = "Add ideas choins"

    def accept_selected_idea(self, request, queryset):
        for idea_choins in queryset:
            accept_idea(idea_choins)
            [update_idea_choins(idea) for idea in models.IdeaChoin.objects.all()]


@admin.register(models.UserIdeaChoin)
class UserIdeaChoinAdmin(admin.ModelAdmin):
    list_display = ("user", "idea", "choins")


@admin.register(models.ChoinEvent)
class ChoinEventAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "module",
        "display_content",
        "balance",
        "created_at",
    )

    def display_content(self, obj):
        # Adjust the number (e.g., 50) based on how many characters you want to display
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    display_content.short_description = "Content"


@admin.register(models.ProjectChoin)
class ProjectChoinAdmin(admin.ModelAdmin):
    pass

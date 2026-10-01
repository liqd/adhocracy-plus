from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic import ListView
from wagtail.models import Page

from .models import LearningCategory
from .models import LearningNuggetPage


class AjaxTemplateMixin:
    """Mixin to handle AJAX template selection"""

    ajax_template_name = None

    def get_template_names(self):
        if self.request.is_ajax and self.ajax_template_name:
            return [self.ajax_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_ajax"] = self.request.is_ajax  # Add is_ajax flag to context
        return context


class LearningCenterView(AjaxTemplateMixin, ListView):
    template_name = "a4_candy_learning_nuggets/learning_center.html"
    ajax_template_name = "a4_candy_learning_nuggets/includes/nuggets_index.html"
    context_object_name = "grouped_categories"
    model = LearningCategory

    PERMISSION_ORDER = ["teilnehmer:in", "initiator:in", "moderator:in"]

    def get_queryset(self):
        return super().get_queryset().order_by("order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = list(context.get("grouped_categories", []))

        grouped = {}
        for category in categories:
            grouped.setdefault(category.permission_level, []).append(category)

        grouped_categories = []
        for perm_level in self.PERMISSION_ORDER:
            if perm_level in grouped:
                grouped_categories.append(
                    {"permission_level": perm_level, "categories": grouped[perm_level]}
                )

        context["grouped_categories"] = grouped_categories

        if not self.request.is_ajax:
            page = get_object_or_404(Page, slug="learning-center")
            context["page"] = page.specific

        return context


class LearningCategoryView(AjaxTemplateMixin, DetailView):
    """View for a specific category, showing all nuggets in that category"""

    template_name = "a4_candy_learning_nuggets/learning_category.html"
    ajax_template_name = "a4_candy_learning_nuggets/includes/nuggets_list.html"
    context_object_name = "category"

    def get_object(self):
        category = get_object_or_404(
            LearningCategory, slug=self.kwargs["category_slug"]
        )

        return category


class LearningNuggetView(AjaxTemplateMixin, DetailView):
    """View for a specific learning nugget"""

    template_name = "a4_candy_learning_nuggets/learning_nugget_page.html"
    ajax_template_name = "a4_candy_learning_nuggets/includes/nugget_detail.html"
    context_object_name = "nugget"

    def get_object(self):
        # Get the nugget based on the slug, ensuring it belongs to the correct category
        category = get_object_or_404(
            LearningCategory, slug=self.kwargs["category_slug"]
        )
        nugget = get_object_or_404(
            LearningNuggetPage, slug=self.kwargs["nugget_slug"], category=category
        )

        return nugget

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.categories import filters as category_filters
from adhocracy4.exports.views import DashboardExportView
from adhocracy4.filters import filters as a4_filters
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from apps.contrib.widgets import AplusOrderingWidget
from apps.ideas import views as idea_views
from apps.organisations.mixins import UserFormViewMixin

from . import forms
from . import models


def get_ordering_choices(view):
    choices = (("-created", _("Most recent")),)
    if view.module.has_feature("rate", models.MapIdea):
        choices += (("-positive_rating_count", _("Most popular")),)
    choices += (("-comment_count", _("Most commented")),)
    return choices


class MapIdeaFilterSet(a4_filters.DefaultsFilterSet):
    defaults = {"ordering": "-created"}
    category = category_filters.CategoryFilter()
    ordering = a4_filters.DynamicChoicesOrderingFilter(
        choices=get_ordering_choices, widget=AplusOrderingWidget
    )

    class Meta:
        model = models.MapIdea
        fields = ["category"]


class MapIdeaListView(idea_views.AbstractIdeaListView, DisplayProjectOrModuleMixin):
    model = models.MapIdea
    filter_set = MapIdeaFilterSet

    def dispatch(self, request, **kwargs):
        self.mode = request.GET.get("mode", "map")
        if self.mode == "map":
            self.paginate_by = 0
        else:
            page_size = int(request.GET.get("page_size", 20))
            page_size = 0 if page_size < 0 else page_size
            self.paginate_by = page_size
        return super().dispatch(request, **kwargs)


class MapIdeaDetailView(idea_views.AbstractIdeaDetailView):
    model = models.MapIdea
    queryset = (
        models.MapIdea.objects.annotate_positive_rating_count().annotate_negative_rating_count()
    )
    permission_required = "a4_candy_mapideas.view_mapidea"


class MapIdeaCreateView(idea_views.AbstractIdeaCreateView, UserFormViewMixin):
    model = models.MapIdea
    form_class = forms.MapIdeaForm
    permission_required = "a4_candy_mapideas.add_mapidea"
    template_name = "a4_candy_mapideas/mapidea_create_form.html"


class MapIdeaUpdateView(idea_views.AbstractIdeaUpdateView, UserFormViewMixin):
    model = models.MapIdea
    form_class = forms.MapIdeaForm
    permission_required = "a4_candy_mapideas.change_mapidea"
    template_name = "a4_candy_mapideas/mapidea_update_form.html"


class MapIdeaDeleteView(idea_views.AbstractIdeaDeleteView):
    model = models.MapIdea
    success_message = _("Your Idea has been deleted")
    permission_required = "a4_candy_mapideas.change_mapidea"
    template_name = "a4_candy_mapideas/mapidea_confirm_delete.html"


class MapIdeaModerateView(idea_views.AbstractIdeaModerateView):
    model = models.MapIdea
    permission_required = "a4_candy_mapideas.moderate_mapidea"
    template_name = "a4_candy_mapideas/mapidea_moderate_form.html"
    moderateable_form_class = forms.MapIdeaModerateForm


class MapIdeaDashboardExportView(DashboardExportView):
    template_name = "a4exports/export_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["export"] = reverse(
            "a4dashboard:mapidea-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        context["comment_export"] = reverse(
            "a4dashboard:mapidea-comment-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        return context

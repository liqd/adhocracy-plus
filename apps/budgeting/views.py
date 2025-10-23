import re

import django_filters
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.categories import filters as category_filters
from adhocracy4.exports.views import DashboardExportView
from adhocracy4.filters import filters as a4_filters
from adhocracy4.filters.widgets import DropdownLinkWidget
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from apps.contrib.widgets import AplusOrderingWidget
from apps.ideas import views as idea_views
from apps.organisations.mixins import UserFormViewMixin

from . import forms
from . import models


def get_ordering_choices(view):
    choices = (("-created", _("Most recent")),)
    if view.module.has_feature("rate", models.Proposal):
        choices += (("-positive_rating_count", _("Most popular")),)
    choices += (("-comment_count", _("Most commented")),)
    return choices


class ArchivedWidget(DropdownLinkWidget):
    label = _("Archived")

    def __init__(self, attrs=None):
        choices = (
            ("", _("All")),
            ("false", _("No")),
            ("true", _("Yes")),
        )
        super().__init__(attrs, choices)


class ProposalFilterSet(a4_filters.DefaultsFilterSet):
    defaults = {"ordering": "-created", "is_archived": "false"}
    category = category_filters.CategoryFilter()
    ordering = a4_filters.DynamicChoicesOrderingFilter(
        choices=get_ordering_choices, widget=AplusOrderingWidget
    )
    is_archived = django_filters.BooleanFilter(widget=ArchivedWidget)

    class Meta:
        model = models.Proposal
        fields = ["category", "is_archived"]


class ProposalListView(idea_views.AbstractIdeaListView, DisplayProjectOrModuleMixin):
    model = models.Proposal
    filter_set = ProposalFilterSet
    paginate_by = 0  # Maps need all ideas, pagination is handled in get_context_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ua = self.request.headers.get("User-Agent", "")
        is_mobile = bool(re.search(r"Mobi|Android|iPhone|iPod|Windows Phone", ua, re.I))
        page_size = int(self.request.GET.get("page_size", 15 if is_mobile else 8))
        self.mode = self.request.GET.get("mode", "map")
        object_list = context.get("object_list", [])

        if page_size > 0:
            paginator = Paginator(object_list, page_size)
            page = int(self.request.GET.get("page", 1))
            try:
                paginated_list = paginator.page(page)
            except EmptyPage:
                paginated_list = paginator.page(paginator.num_pages)
        else:
            paginated_list = object_list
        context["paginated_list"] = paginated_list
        context["page_obj"] = paginated_list  # page_obj ist die paginierte Liste selbst
        context["is_paginated"] = paginator.num_pages > 1 if page_size > 0 else False
        return context


class ProposalDetailView(idea_views.AbstractIdeaDetailView):
    model = models.Proposal
    queryset = (
        models.Proposal.objects.annotate_positive_rating_count().annotate_negative_rating_count()
    )
    permission_required = "a4_candy_budgeting.view_proposal"


class ProposalCreateView(idea_views.AbstractIdeaCreateView, UserFormViewMixin):
    model = models.Proposal
    form_class = forms.ProposalForm
    permission_required = "a4_candy_budgeting.add_proposal"
    template_name = "a4_candy_budgeting/proposal_create_form.html"


class ProposalUpdateView(idea_views.AbstractIdeaUpdateView, UserFormViewMixin):
    model = models.Proposal
    form_class = forms.ProposalForm
    permission_required = "a4_candy_budgeting.change_proposal"
    template_name = "a4_candy_budgeting/proposal_update_form.html"


class ProposalDeleteView(idea_views.AbstractIdeaDeleteView):
    model = models.Proposal
    success_message = _("Your budget request has been deleted")
    permission_required = "a4_candy_budgeting.change_proposal"
    template_name = "a4_candy_budgeting/proposal_confirm_delete.html"


class ProposalModerateView(idea_views.AbstractIdeaModerateView):
    model = models.Proposal
    permission_required = "a4_candy_budgeting.moderate_proposal"
    template_name = "a4_candy_budgeting/proposal_moderate_form.html"
    moderateable_form_class = forms.ProposalModerateForm


class ProposalDashboardExportView(DashboardExportView):
    template_name = "a4exports/export_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["export"] = reverse(
            "a4dashboard:budgeting-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        context["comment_export"] = reverse(
            "a4dashboard:budgeting-comment-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        return context

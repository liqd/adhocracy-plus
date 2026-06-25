import json
from types import SimpleNamespace

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views import View

from adhocracy4.projects.models import Project
from apps.contrib.mixins import StaffRequiredMixin

from .export_utils.core import generate_full_export
from .playground_errors import format_playground_exception
from .pydantic_models import DocumentInputItem
from .pydantic_models import ProjectSummaryResponse
from .services import AIService
from .services import SummaryRequest


def _get_projects_queryset():
    """Projects for the test page dropdown (non-draft, ordered)."""
    return (
        Project.objects.filter(is_draft=False)
        .select_related("organisation")
        .order_by("organisation__name", "name")
    )


def _get_provider_choices():
    """Provider choices for summarization test dropdowns from AI_PROVIDERS."""
    providers = getattr(settings, "AI_PROVIDERS", {})
    return [
        {
            "handle": handle,
            "label": cfg.get("display_name") or handle.replace("_", " ").title(),
        }
        for handle, cfg in providers.items()
    ]


class SummarizationTestExportView(StaffRequiredMixin, View):
    """Return project export JSON for the summarization test page."""

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        export_data = generate_full_export(project)
        return HttpResponse(
            json.dumps(export_data, indent=2),
            content_type="application/json",
        )


class SummarizationTestView(StaffRequiredMixin, View):
    """Simple test view for summarization service."""

    def get(self, request):
        """Display test form."""
        default_prompt = SummaryRequest.DEFAULT_PROMPT
        default_provider = getattr(settings, "AI_PROVIDER", "ovhcloud")
        context = {
            "default_prompt": default_prompt,
            "projects": _get_projects_queryset(),
            "providers": _get_provider_choices(),
            "provider": default_provider,
        }
        return render(request, "summarization/test.html", context)

    def _handle_text_request(
        self, text: str, prompt: str, provider_handle: str | None
    ) -> tuple[ProjectSummaryResponse | None, int, str | None]:
        """Handle text-only summarization."""
        try:
            service = AIService(provider_handle=provider_handle)
            response = service.summarize(
                text=text,
                prompt=prompt if prompt else None,
                result_type=ProjectSummaryResponse,
            )
            return response, len(text), None
        except BaseException as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
                raise
            return None, 0, format_playground_exception(e)

    def _extract_project_from_json(self, text: str):
        """Extract project information from JSON text if available."""
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "project" in data:
                project_data = data["project"]
                # Create a simple mock project object with needed attributes
                project = SimpleNamespace()
                project.slug = project_data.get("slug", "test-project")
                project.pk = project_data.get("id", 1)
                project.result = project_data.get("result", "")
                project.name = project_data.get("name", "Test Project")

                # Create mock organisation
                org = SimpleNamespace()
                org_data = project_data.get("organisation", "test-org")
                if isinstance(org_data, dict):
                    org.slug = org_data.get("slug", "test-org")
                else:
                    # If organisation is just a string (name), use it as slug
                    org.slug = str(org_data).lower().replace(" ", "-")
                project.organisation = org

                # Mock get_absolute_url method
                def get_absolute_url():
                    return f"/projects/{project.slug}/"

                project.get_absolute_url = get_absolute_url

                # Mock modules queryset for _summary_section.html
                # The template uses project.modules|get_module_by_id filter
                class MockModules:
                    def filter(self, id=None):
                        return self

                    def first(self):
                        return None

                project.modules = MockModules()

                return project
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass
        return None

    def post(self, request):
        """Process summarization request."""
        text = request.POST.get("text", "")
        prompt = request.POST.get("prompt", "")
        provider_handle = request.POST.get("provider", None)
        project_id = request.POST.get("project_id", "").strip()

        default_provider = getattr(settings, "AI_PROVIDER", "ovhcloud")
        context = {
            "text": text,
            "prompt": prompt,
            "default_prompt": SummaryRequest.DEFAULT_PROMPT,
            "provider": provider_handle or default_provider,
            "providers": _get_provider_choices(),
            "summary_response": None,
            "error": None,
            "original_length": 0,
            "project": None,
            "projects": _get_projects_queryset(),
        }

        # Use real project from dropdown if project_id was submitted
        if project_id:
            try:
                context["project"] = get_object_or_404(Project, id=int(project_id))
                context["selected_project_id"] = int(project_id)
            except (ValueError, TypeError):
                pass
        elif text:
            # Fallback: extract mock project from JSON text
            project = self._extract_project_from_json(text)
            if project:
                context["project"] = project

        if text:
            response, original_length, error = self._handle_text_request(
                text=text,
                prompt=prompt,
                provider_handle=provider_handle,
            )
            context["summary_response"] = response
            context["original_length"] = original_length
            context["error"] = error

        return render(request, "summarization/test.html", context)


class DocumentSummarizationTestView(StaffRequiredMixin, View):
    """Test view for document summarization with handles."""

    def get(self, request):
        """Display test form."""
        default_provider = getattr(settings, "AI_DOCUMENT_PROVIDER", "ovhcloud")
        context = {
            "providers": _get_provider_choices(),
            "provider": default_provider,
        }
        return render(request, "summarization/test_documents.html", context)

    def post(self, request):
        """Process document summarization request."""
        prompt = request.POST.get("prompt", "")
        provider_handle = request.POST.get("provider", None)
        if provider_handle == "":
            provider_handle = None
        documents_json = request.POST.get("documents", "")

        default_provider = getattr(settings, "AI_DOCUMENT_PROVIDER", "ovhcloud")
        context = {
            "prompt": prompt,
            "provider": provider_handle or default_provider,
            "providers": _get_provider_choices(),
            "documents_json": documents_json,
            "summary_response": None,
            "error": None,
        }

        if documents_json:
            try:
                import json

                # Parse JSON input
                documents_data = json.loads(documents_json)

                # Convert to list of DocumentInputItem
                if isinstance(documents_data, dict):
                    # If it's a dict, convert to list format
                    documents = [
                        DocumentInputItem(handle=handle, url=url)
                        for handle, url in documents_data.items()
                    ]
                elif isinstance(documents_data, list):
                    # If it's already a list
                    documents = [
                        DocumentInputItem(**doc) if isinstance(doc, dict) else doc
                        for doc in documents_data
                    ]
                else:
                    raise ValueError("Documents must be a dict or list")

                # Process documents
                service = AIService(document_provider_handle=provider_handle)
                response = service.request_vision(
                    documents=documents,
                    prompt=prompt if prompt else None,
                )
                context["summary_response"] = response

            except json.JSONDecodeError as e:
                context["error"] = format_playground_exception(e)
            except Exception as e:
                context["error"] = format_playground_exception(e)
        else:
            context["error"] = "Please provide documents in JSON format"

        return render(request, "summarization/test_documents.html", context)

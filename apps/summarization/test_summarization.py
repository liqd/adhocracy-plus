#!/usr/bin/env python
"""
Test script for summarization service.

Usage:
    python manage.py shell < apps/summarization/test_summarization.py
    # or
    python apps/summarization/test_summarization.py --provider openrouter
"""

import argparse
import os
import sys

# Setup Django environment if running as standalone script
if __name__ == "__main__" and not os.environ.get("DJANGO_SETTINGS_MODULE"):
    # Add project root to Python path so adhocracy-plus module can be found
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adhocracy-plus.config.settings")
    import django

    django.setup()

from adhocracy4.projects.models import Project
from apps.summarization.pydantic_models import SummaryResponse
from apps.summarization.services import AIService

# Long example text for testing
LONG_TEXT = (
    """
Artificial intelligence has made enormous progress in recent years and is now used in many areas.
From speech processing to image analysis to predictions and decision support - AI systems are finding
application in almost all industries.

The development of Large Language Models (LLMs) such as GPT, Claude or DeepSeek has revolutionized the possibilities of
text processing. These models can understand, generate and summarize texts, which
opens up numerous use cases.

OpenRouter.ai provides centralized access to various AI models via a unified API.
This significantly simplifies the integration of AI functions into applications, as developers do not need to
implement a separate integration for each provider.

OVHcloud provides secure AI endpoints that enable companies to use AI models without
their data being used for training. This is particularly important for companies with strict
data protection requirements.

RouterLab provides access to various AI models such as Kimi K2.5, which are specifically optimized for certain use cases.
The platform enables developers to quickly test and compare different models.

Text summarization is one of the most common applications of AI systems. It enables
long documents to be quickly captured, important information extracted and content presented compactly.
This is particularly useful for research, content creation and knowledge management.

Modern summarization algorithms use various techniques, from simple extraction methods to
abstractive approaches that generate new formulations. The quality of summaries depends
on many factors, including the complexity of the original text, the desired length and the
model used.

The integration of AI summarization functions into web applications requires careful planning.
Developers must consider aspects such as latency, costs, data protection and user-friendliness.
Flexible provider abstractions enable the use of different backends without changing the application logic.
"""
    * 2
)  # Repeat to make it even longer


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def _run_validations(summary: str, original_length: int) -> tuple[list[str], list[str]]:
    """Run validation checks on summary."""
    validations_passed = []
    validations_failed = []

    if len(summary) < original_length:
        validations_passed.append("Summary is shorter than original")
    else:
        validations_failed.append("Summary is not shorter than original")

    if len(summary) > 0:
        validations_passed.append("Summary is not empty")
    else:
        validations_failed.append("Summary is empty")

    # Check for relevant keywords
    keywords = ["AI", "summary", "models", "text", "systems", "application"]
    found_keywords = [kw for kw in keywords if kw.lower() in summary.lower()]
    if found_keywords:
        validations_passed.append(
            f"Contains relevant keywords: {', '.join(found_keywords)}"
        )
    else:
        validations_failed.append("Does not contain relevant keywords")

    return validations_passed, validations_failed


def _print_statistics(summary: str, original_length: int):
    """Print statistics about the summary."""
    compression_ratio = (len(summary) / original_length) * 100 if original_length else 0
    reduction = original_length - len(summary)

    print("STATISTICS:")
    print(f"  Original Length:       {original_length} characters")
    print(f"  Summary Length:        {len(summary)} characters")
    print(f"  Compression:           {compression_ratio:.2f}%")
    print(f"  Reduction:             {reduction} characters")
    print_separator()


def _print_service_info(service):
    """Print service configuration information."""
    print("Initializing service...")
    print("✓ Service successfully initialized")
    print(f"  Model: {service.provider.config.model_name}")
    print(f"  Base URL: {service.provider.config.base_url}")
    api_key = service.provider.config.api_key
    if api_key:
        masked_key = api_key[:10] + "..." if len(api_key) > 10 else "***"
        print(f"  API Key: {masked_key}")
    print_separator()


def _print_summary_results(response: SummaryResponse, long_text: str):
    """Print summary results and key points."""
    if response.summary_items:
        print("SUMMARY ITEMS:")
        print("-" * 80)
        for item in response.summary_items:
            print(f"\nTitle: {item.title}")
            print(f"Summary: {item.summary}")
            if item.key_points:
                print("Key Points:")
                for i, point in enumerate(item.key_points, 1):
                    print(f"  {i}. {point}")
        print_separator()

    if response.module_items:
        print("MODULE ITEMS:")
        print("-" * 80)
        for module in response.module_items:
            print(f"\nModule: {module.module_name}")
            print(f"Phase Status: {module.phase_status}")
            print(f"Summary: {module.summary}")
            if module.key_points:
                print("Key Points:")
                for i, point in enumerate(module.key_points, 1):
                    print(f"  {i}. {point}")
        print_separator()

    # Calculate total summary length
    total_length = sum(len(item.summary) for item in response.summary_items)
    if total_length > 0:
        print("STATISTICS:")
        print(f"  Original Length:       {len(long_text)} characters")
        print(f"  Total Summary Length:  {total_length} characters")
        compression_ratio = (
            (total_length / len(long_text)) * 100 if len(long_text) else 0
        )
        reduction = len(long_text) - total_length
        print(f"  Compression:           {compression_ratio:.2f}%")
        print(f"  Reduction:             {reduction} characters")
        print_separator()


def _get_or_create_test_project():
    """Get existing project or create a test project."""
    project = Project.objects.first()
    if project:
        return project

    print("No project found. Creating a test project...")
    try:
        from django.contrib.auth import get_user_model

        from apps.organisations.models import Organisation

        User = get_user_model()

        organisation = Organisation.objects.first()
        if not organisation:
            organisation = Organisation.objects.create(
                name="Test Organisation",
                description="Test organisation for summarization",
            )
            user = User.objects.first()
            if user:
                organisation.initiators.add(user)
            print(f"✓ Created test organisation: {organisation.name}")

        project = Project.objects.create(
            name="Test Project",
            description="Test project for summarization",
            organisation=organisation,
        )
        print(f"✓ Created test project: {project.name}")
        return project
    except Exception as e:
        print(f"Could not create test project: {e}")
        import traceback

        traceback.print_exc()
        print(
            "\nPlease create a project manually in the admin or use an existing project."
        )
        sys.exit(1)


def _validate_response(response: SummaryResponse, original_length: int):
    """Validate the summary response."""
    validations_passed = []
    validations_failed = []

    if not response.summary_items:
        validations_failed.append("No summary items generated")
        return validations_passed, validations_failed

    total_summary_length = sum(len(item.summary) for item in response.summary_items)
    if total_summary_length < original_length:
        validations_passed.append("Summary is shorter than original")
    else:
        validations_failed.append("Summary is not shorter than original")

    if total_summary_length > 0:
        validations_passed.append("Summary is not empty")
    else:
        validations_failed.append("Summary is empty")

    validations_passed.append(f"Summary contains {len(response.summary_items)} items")
    if response.module_items:
        validations_passed.append(f"Module contains {len(response.module_items)} items")

    return validations_passed, validations_failed


def test_summarization(provider_handle: str = None):
    """Test the summarization service."""
    from django.conf import settings

    print_separator()
    print("AI SUMMARIZATION SERVICE TEST")
    print_separator()

    if not provider_handle:
        provider_handle = getattr(settings, "AI_PROVIDER", "openrouter")

    print(f"Provider Handle: {provider_handle}")
    print_separator()

    try:
        service = AIService(provider_handle=provider_handle)
        _print_service_info(service)

        print("ORIGINAL TEXT:")
        print("-" * 80)
        print(LONG_TEXT[:500] + "...")
        print(f"Length: {len(LONG_TEXT)} characters")
        print_separator()

        project = _get_or_create_test_project()

        print("Generating summary with project_summarize...")
        response = service.project_summarize(
            project=project,
            text=LONG_TEXT,
            result_type=SummaryResponse,
            is_rate_limit=False,
        )
        print("✓ Summary successfully created")
        print_separator()

        _print_summary_results(response, LONG_TEXT)

        validations_passed, validations_failed = _validate_response(
            response, len(LONG_TEXT)
        )

        print("VALIDATION:")
        for validation in validations_passed:
            print(f"  ✓ {validation}")
        for validation in validations_failed:
            print(f"  ✗ {validation}")
        print_separator()

        if not validations_failed:
            print("✓ ALL VALIDATIONS PASSED")
        else:
            print("✗ SOME VALIDATIONS FAILED")

        print_separator()

    except ValueError as e:
        print(f"ERROR during configuration or initialization: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR during summary generation: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test script for summarization service"
    )
    parser.add_argument(
        "--provider",
        choices=["openrouter", "ovhcloud", "routerlab"],
        default=None,
        help="Provider handle to use (default: from AI_PROVIDER setting or 'openrouter')",
    )
    args = parser.parse_args()

    test_summarization(provider_handle=args.provider)


# Execute when run directly or via manage.py shell
# When run via shell < script.py, the code is executed directly
if __name__ == "__main__":
    main()
else:
    # When run via shell < script.py, execute with defaults
    test_summarization()

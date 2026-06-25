"""Provider implementation for AI services."""

import logging
from abc import ABC
from typing import TypeVar
from typing import cast

from django.conf import settings
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai import ImageUrl
from pydantic_ai import TextOutput
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.providers.openai import OpenAIProvider
from sentry_sdk import capture_exception

from .llm_json import parse_structured_llm_json
from .pydantic_models import DocumentSummaryResponse
from .sentry_tags import ensure_sentry_project_tags

logger = logging.getLogger(__name__)

TModel = TypeVar("TModel", bound=BaseModel)


def _make_json_parse_fn(result_type: type[TModel]):
    def parse(text: str) -> TModel:
        return parse_structured_llm_json(text, result_type)

    return parse


class ProviderConfig:
    """Configuration for an AI provider."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        base_url: str,
        handle: str,
        supports_images: bool = True,
        supports_documents: bool = False,
    ):
        """
        Initialize provider configuration.

        Args:
            api_key: API key for the provider
            model_name: Name of the model to use
            base_url: Base URL for the API
            handle: Unique identifier/name for this provider configuration
            supports_images: Whether this provider supports image processing via vision API
            supports_documents: Whether this provider supports document processing (PDFs, etc.)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self.handle = handle
        self.supports_images = supports_images
        self.supports_documents = supports_documents

    @classmethod
    def from_handle(cls, handle: str) -> "ProviderConfig":
        """
        Create ProviderConfig from handle by loading configuration from Django settings.

        Args:
            handle: Handle/name of the provider configuration

        Returns:
            ProviderConfig instance

        Raises:
            ValueError: If provider configuration is missing or invalid
        """
        # Get provider configurations from settings
        provider_configs = getattr(settings, "AI_PROVIDERS", {})

        if not provider_configs:
            raise ValueError(
                "AI_PROVIDERS not configured. " "Please configure providers in local.py"
            )

        if handle not in provider_configs:
            available = ", ".join(provider_configs.keys())
            raise ValueError(
                f"Unknown provider handle: {handle}. "
                f"Available providers: {available}"
            )

        config_dict = provider_configs[handle]

        # Validate required fields
        required_fields = ["api_key", "model_name", "base_url"]
        missing_fields = [
            field for field in required_fields if field not in config_dict
        ]
        if missing_fields:
            raise ValueError(
                f"Provider configuration '{handle}' is missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        return cls(
            api_key=config_dict["api_key"],
            model_name=config_dict["model_name"],
            base_url=config_dict["base_url"],
            handle=handle,
            supports_images=config_dict.get("supports_images", True),
            supports_documents=config_dict.get("supports_documents", False),
        )


class AIRequest(ABC):
    vision_support = False

    def prompt(self) -> str:
        raise NotImplementedError("Subclasses must implement prompt()")


class AIProvider:
    """Unified provider for AI services using OpenAI-compatible APIs."""

    def __init__(self, config: ProviderConfig):
        """
        Initialize AI provider.

        Args:
            config: Provider configuration object
        """
        self.config = config

        self.system_prompt = getattr(
            settings,
            "SYSTEM_PROMPT",
            "",
        )

        # Use MistralProvider for Mistral, OpenAIProvider for others
        if config.handle == "mistral":
            self.provider = MistralProvider(
                api_key=config.api_key,
                base_url=config.base_url,
            )
            self.is_mistral = True
        else:
            # All other providers are OpenAI-compatible
            self.provider = OpenAIProvider(
                base_url=config.base_url,
                api_key=config.api_key,
            )
            self.is_mistral = False

    def _set_provider_handle(self, response: BaseModel) -> None:
        """
        Set provider handle on response if it has a provider field.

        Args:
            response: Response object to modify
        """
        if hasattr(response, "provider"):
            response.provider = self.config.handle

    def text_request(
        self, request: AIRequest, result_type: type[BaseModel]
    ) -> BaseModel:
        """
        Execute a text request with structured input and output.

        Args:
            request: Pydantic BaseModel with request data
            result_type: Pydantic BaseModel class for structured output

        Returns:
            Structured response as BaseModel instance
        """
        # Use MistralModel for Mistral, OpenAIChatModel for others
        if self.is_mistral:
            model = MistralModel(
                self.config.model_name,
                provider=self.provider,
            )
        else:
            model = OpenAIChatModel(
                model_name=self.config.model_name,
                provider=self.provider,
            )

        agent = Agent(
            model=model,
            system_prompt=self.system_prompt,
            output_type=TextOutput(_make_json_parse_fn(result_type)),
            tools=[],
        )

        try:
            ensure_sentry_project_tags()
            result = agent.run_sync(request.prompt())
            response = result.output

            self._set_provider_handle(response)

            return response
        except Exception as e:
            logger.error(
                f"AI text request failed with provider {self.config.handle} (model: {self.config.model_name}): {str(e)}",
                exc_info=True,
            )
            capture_exception(e)
            raise

    # Deprecate ? And Use text_request or vision_request instead ?
    def request(self, request: AIRequest, result_type: type[BaseModel]) -> BaseModel:
        """
        Automatically determines if it's a text or multimodal request.
        """
        # TODO: Check if the PROVIDER supports multimodal requests, or switch the Provider automaticly ?
        # Check if request supports vision (multimodal request)
        if getattr(request, "vision_support", False):
            image_urls = getattr(request, "image_urls", None) or []
            if not issubclass(result_type, DocumentSummaryResponse):
                raise TypeError(
                    "Vision requests require result_type to be DocumentSummaryResponse or a subclass."
                )
            return self.multimodal_request(
                request, cast(type[DocumentSummaryResponse], result_type), image_urls
            )
        else:
            return self.text_request(request, result_type)

    # Rename to vision_request instead and use only DocumentSummaryResponse for the result type?
    def multimodal_request(
        self,
        request: AIRequest,
        result_type: type[DocumentSummaryResponse],
        image_urls: list[str],
    ) -> DocumentSummaryResponse:
        """
        Execute a multimodal request with images using vision API.

        Args:
            request: Pydantic BaseModel with request data
            result_type: DocumentSummaryResponse (or a subclass at runtime)
            image_urls: List of image URLs to include in the request

        Returns:
            Structured response instance
        """
        # Use MistralModel for Mistral, OpenAIChatModel for others
        # Note: Mistral may not support vision/multimodal requests
        # Note: OpenAIResponsesModel uses /v1/responses endpoint which is not supported by all providers
        # Use OpenAIChatModel instead for better compatibility
        if self.is_mistral:
            model = MistralModel(
                self.config.model_name,
                provider=self.provider,
            )
        else:
            # Use OpenAIChatModel for image requests (better compatibility with OpenAI-compatible APIs)
            model = OpenAIChatModel(
                model_name=self.config.model_name,
                provider=self.provider,
            )

        agent = Agent(
            model=model,
            system_prompt=self.system_prompt,
            output_type=TextOutput(_make_json_parse_fn(result_type)),
            output_retries=3,
            tools=[],
        )

        # Build user content with prompt and image URLs
        # Filter URLs to only include supported formats
        # Both Mistral and OpenAI-compatible providers support images and PDFs
        supported_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".mpo",
            ".heif",
            ".avif",
            ".bmp",
            ".tiff",
            ".tif",
            ".pdf",  # PDFs supported by Mistral Vision and OpenAI-compatible providers
        )

        filtered_urls = []
        for url in image_urls:
            url_lower = url.lower()
            # Check if URL ends with supported extension
            if any(url_lower.endswith(ext) for ext in supported_extensions):
                filtered_urls.append(url)

        user_content = [request.prompt()]
        for url in filtered_urls:
            user_content.append(ImageUrl(url=url))

        try:
            ensure_sentry_project_tags()
            result = agent.run_sync(user_content)
            response = result.output

            self._set_provider_handle(response)

            return response
        except Exception as e:
            logger.error(
                f"AI multimodal request failed with provider {self.config.handle} (model: {self.config.model_name}, "
                f"images: {len(filtered_urls)}): {str(e)}",
                exc_info=True,
            )
            capture_exception(e)
            raise

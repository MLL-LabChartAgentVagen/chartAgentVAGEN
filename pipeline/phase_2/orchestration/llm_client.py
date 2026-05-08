"""
Unified LLM Client with multi-provider parameter adaptation.

Salvaged from generation_pipeline.py §6 (L1682–2068).

Supported providers:
- OpenAI: GPT-4, GPT-3.5-turbo, o1, o3, etc.
- Gemini: gemini-1.5-pro, gemini-2.0-flash, etc. (via OpenAI SDK)
- Gemini Native: Using google-genai SDK
- Azure OpenAI: Azure-hosted OpenAI models
- Custom: Any OpenAI API-compatible service
"""

import json
import re
from dataclasses import dataclass
from typing import Any, NamedTuple, Optional


# =============================================================================
# Token Usage / Structured Response
# =============================================================================

class TokenUsage(NamedTuple):
    """Per-call token accounting reported by the LLM provider."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(NamedTuple):
    """Structured generation result carrying both text and token usage."""
    code: str
    token_usage: Optional[TokenUsage]


def _extract_token_usage(response: Any, provider: str) -> Optional[TokenUsage]:
    """Extract token counts from a provider response.

    Returns None if the provider did not report usage (older SDK, mock
    client, partial failure, etc.) — callers must treat None as a
    graceful-degradation signal (counts as 0 against any budget).
    """
    try:
        if provider == "gemini-native":
            meta = getattr(response, "usage_metadata", None)
            if meta is None:
                return None
            prompt = getattr(meta, "prompt_token_count", None) or 0
            completion = getattr(meta, "candidates_token_count", None) or 0
            total = getattr(meta, "total_token_count", None)
            if total is None:
                total = prompt + completion
            return TokenUsage(int(prompt), int(completion), int(total))

        # OpenAI / Azure / Gemini-via-OpenAI all expose `.usage` on the
        # ChatCompletion result. Fields are prompt_tokens / completion_tokens
        # / total_tokens.
        usage = getattr(response, "usage", None)
        if usage is None:
            return None
        prompt = getattr(usage, "prompt_tokens", None) or 0
        completion = getattr(usage, "completion_tokens", None) or 0
        total = getattr(usage, "total_tokens", None)
        if total is None:
            total = prompt + completion
        return TokenUsage(int(prompt), int(completion), int(total))
    except Exception:
        return None


# =============================================================================
# Provider Capabilities
# =============================================================================

@dataclass
class ProviderCapabilities:
    """Define what parameters each provider supports."""
    supports_temperature: bool = True
    supports_max_tokens: bool = True
    supports_max_completion_tokens: bool = False
    supports_response_format: bool = True
    supports_json_mode: bool = True

    # Token parameter name to use
    token_param_name: str = "max_tokens"

    # Temperature constraints
    min_temperature: float = 0.0
    max_temperature: float = 2.0
    default_temperature: float = 1.0

    # Special handling flags
    requires_json_in_prompt: bool = False
    is_reasoning_model: bool = False


# Provider capability definitions
PROVIDER_CAPABILITIES = {
    "openai": ProviderCapabilities(
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=True,
        supports_json_mode=True,
    ),
    "gemini": ProviderCapabilities(
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
    "gemini-native": ProviderCapabilities(
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
    "azure": ProviderCapabilities(
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=True,
        supports_json_mode=True,
    ),
    "custom": ProviderCapabilities(
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
}


# Model-specific overrides (for models with special requirements)
MODEL_OVERRIDES = {
    "o1": ProviderCapabilities(
        supports_temperature=False,
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
    "o3": ProviderCapabilities(
        supports_temperature=False,
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
    "gpt-5": ProviderCapabilities(
        supports_temperature=False,
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
}


def get_provider_capabilities(provider: str, model: str) -> ProviderCapabilities:
    """
    Get capability configuration for a specific provider and model.

    Checks model-specific overrides first, then falls back to provider defaults.
    """
    model_lower = model.lower()
    for model_pattern, capabilities in MODEL_OVERRIDES.items():
        if model_pattern in model_lower:
            return capabilities

    return PROVIDER_CAPABILITIES.get(provider, PROVIDER_CAPABILITIES["custom"])


# =============================================================================
# Parameter Adapter
# =============================================================================

class ParameterAdapter:
    """
    Adapts API call parameters to match provider capabilities.

    This class ensures that only supported parameters are included in API calls,
    avoiding the need for retry-based error handling.
    """

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.capabilities = get_provider_capabilities(provider, model)

    def adapt_parameters(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "json"
    ) -> tuple[dict, list[dict]]:
        """
        Adapt parameters to match provider capabilities.

        Returns:
            (kwargs, modified_messages): API call kwargs and potentially modified messages
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        modified_messages = messages.copy()

        # Add temperature if supported
        if self.capabilities.supports_temperature:
            clamped_temp = max(
                self.capabilities.min_temperature,
                min(temperature, self.capabilities.max_temperature)
            )
            kwargs["temperature"] = clamped_temp

        # Add token limit parameter
        if self.capabilities.supports_max_tokens:
            kwargs[self.capabilities.token_param_name] = max_tokens

        # Handle JSON response format
        if response_format == "json":
            if self.capabilities.supports_json_mode and self.capabilities.supports_response_format:
                kwargs["response_format"] = {"type": "json_object"}
            elif self.capabilities.requires_json_in_prompt:
                modified_messages = messages.copy()
                modified_messages[-1] = modified_messages[-1].copy()
                modified_messages[-1]["content"] += (
                    "\n\nRespond with valid JSON only, no markdown formatting."
                )

        return kwargs, modified_messages


# =============================================================================
# Unified LLM Client
# =============================================================================

class LLMClient:
    """
    Unified LLM client supporting multiple providers with proper parameter adaptation.

    Usage:
        # OpenAI
        client = LLMClient(api_key="sk-...", model="gpt-4", provider="openai")

        # Gemini (via OpenAI API)
        client = LLMClient(
            api_key="your-gemini-key",
            model="gemini-2.0-flash-lite",
            provider="gemini"
        )

        # Gemini (native SDK)
        client = LLMClient(
            api_key="your-gemini-key",
            model="gemini-2.0-flash-lite",
            provider="gemini-native"
        )
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-lite",
        base_url: Optional[str] = None,
        provider: str = "auto"
    ):
        """
        Initialize LLM client with automatic parameter adaptation.

        Args:
            api_key: API key for the provider
            model: Model name
            base_url: Custom API endpoint URL (optional)
            provider: Provider type ("auto", "openai", "gemini",
                      "gemini-native", "azure", "custom")
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None
        self._native_client = None

        # Auto-detect provider from model name if needed
        if provider == "auto":
            if "gemini" in model.lower():
                self.provider = "gemini-native"
            elif "gpt" in model.lower() or "o1" in model.lower() or "o3" in model.lower():
                self.provider = "openai"
            elif "claude" in model.lower():
                self.provider = "openai"  # Claude via compatibility layer
            else:
                self.provider = "custom"
        else:
            self.provider = provider

        # Initialize parameter adapter
        self.adapter = ParameterAdapter(self.provider, self.model)

        # Set base URL based on provider
        if self.provider == "gemini":
            if not self.base_url:
                self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        elif self.provider == "gemini-native":
            self.base_url = None
        elif self.provider == "openai" and not self.base_url:
            self.base_url = "https://api.openai.com/v1"

    def _ensure_client(self):
        """Lazy initialization of API client."""
        if self.provider == "gemini-native":
            if self._native_client is None:
                try:
                    from google import genai
                    self._native_client = genai.Client(api_key=self.api_key)
                except ImportError:
                    raise ImportError(
                        "Please install google-genai for native Gemini support: "
                        "pip install google-genai"
                    )
        else:
            if self._client is None:
                try:
                    from openai import OpenAI
                    self._client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                except ImportError:
                    raise ImportError(
                        "Please install openai SDK: pip install openai>=1.0.0"
                    )

    def _generate_with_usage(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "json"
    ) -> tuple[str, Optional[TokenUsage]]:
        """Generate text and return (text, token_usage).

        Internal helper used by both ``generate`` (which discards usage)
        and ``generate_code`` (which packages usage into an LLMResponse).
        """
        self._ensure_client()

        if self.provider == "gemini-native":
            full_prompt = f"{system}\n\n---\n\n{user}"

            generation_config = {}
            if self.adapter.capabilities.supports_temperature:
                generation_config["temperature"] = temperature
            if self.adapter.capabilities.supports_max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            if response_format == "json" and self.adapter.capabilities.requires_json_in_prompt:
                full_prompt += "\n\nRespond with valid JSON only, no markdown formatting."

            response = self._native_client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=generation_config
            )

            return response.text, _extract_token_usage(response, self.provider)
        else:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]

            kwargs, modified_messages = self.adapter.adapt_parameters(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )

            kwargs["messages"] = modified_messages

            response = self._client.chat.completions.create(**kwargs)
            return (
                response.choices[0].message.content,
                _extract_token_usage(response, self.provider),
            )

    def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "json"
    ) -> str:
        """
        Generate text response using the configured LLM.

        Parameters are automatically adapted to match provider capabilities.

        Returns:
            Generated text response.
        """
        text, _usage = self._generate_with_usage(
            system, user,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        return text

    def generate_json(self, system: str, user: str, **kwargs) -> dict:
        """Generate and parse JSON response."""
        response = self.generate(system, user, response_format="json", **kwargs)

        # Clean response (remove potential markdown code blocks)
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON response from {self.provider} "
                f"(model: {self.model}). Error: {e}\n"
                f"Response preview: {cleaned[:500]}"
            )

    def generate_code(self, system: str, user: str, **kwargs) -> LLMResponse:
        """
        Generate code response (text mode) with automatic fence stripping.

        Convenience method for Phase 2 SDK code generation.
        Strips ```python ... ``` fences from the response.

        Returns:
            LLMResponse(code, token_usage). ``token_usage`` is ``None``
            if the provider did not report counts.
        """
        text, usage = self._generate_with_usage(
            system, user, response_format="text", **kwargs
        )

        cleaned = text.strip()
        # Strip ```python or ``` fences
        cleaned = re.sub(
            r"^```(?:python)?[ \t]*\n?", "", cleaned, count=1
        )
        cleaned = re.sub(r"\n```\s*$", "", cleaned, count=1)

        return LLMResponse(code=cleaned.strip(), token_usage=usage)

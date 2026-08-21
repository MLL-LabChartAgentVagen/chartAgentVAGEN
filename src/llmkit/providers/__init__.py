"""The provider seam: one protocol, one file per vendor, and the shared checks.

`Provider` is the only place that knows a vendor. Adding one is adding a file
next to this one and a line in `_BY_PREFIX`; nothing above this package changes.

Three things have to mean the same on every vendor, or a comparison across models
is comparing request shapes instead of models:

    image input        an `Image` becomes that vendor's image part, ahead of the text
    structured output  the same JSON schema dict, sent as that vendor's schema field
    reasoning effort   one effort word, mapped to that vendor's own scale

`EFFORTS` is that one word's domain. Each provider maps it and refuses anything
outside it, so an unsupported level is an error here rather than a silently
cheaper answer from the service.

`provider_via` is the other way to reach a model: through an OpenAI-compatible
gateway rather than the vendor's own account. Same model, same request, different
transport -- so it is a fallback when a direct account runs out mid-batch, not a
fourth vendor.
"""

from __future__ import annotations

import os
from typing import Protocol, Sequence

from ..types import LLMError, Message, Response

#: The model used when none is named.
DEFAULT_MODEL = "claude-opus-5"

#: How much reasoning effort to spend on a request. One vocabulary for every
#: vendor; each provider maps it onto its own scale.
Effort = str
EFFORTS = ("low", "medium", "high", "xhigh", "max")


def map_effort(effort: Effort, table: dict[str, str], vendor: str) -> str:
    """Translate the shared effort word into what one vendor calls it."""
    if effort not in table:
        raise LLMError(f"{effort!r} is not an effort level; {vendor} accepts "
                       f"{sorted(table)} through the shared names {list(EFFORTS)}")
    return table[effort]


def check_strict(schema: dict, path: str = "schema") -> None:
    """A schema for structured output must close every object it contains.

    An object that omits `additionalProperties: false` is refused by the service,
    and the refusal names only the innermost field, so a schema written a level
    away from the call is hard to correct. Checking before the request goes out
    names the whole path and costs nothing.
    """
    if schema.get("type") == "object" and schema.get("additionalProperties") is not False:
        raise LLMError(f"`{path}` is an object without `additionalProperties: false`; "
                       "structured output requires it on every object in the schema")
    for key, sub in schema.get("properties", {}).items():
        check_strict(sub, f"{path}.{key}")
    if isinstance(schema.get("items"), dict):
        check_strict(schema["items"], f"{path}[]")


class Provider(Protocol):
    name: str

    def complete(self, *, model: str, system: str, messages: Sequence[Message],
                 max_tokens: int, effort: Effort | None, schema: dict | None,
                 extra: dict) -> Response:
        ...

    def embed(self, texts: Sequence[str], model: str) -> list[list[float]]:
        ...


#: Which vendor a model name belongs to. Read in order, first prefix wins.
_BY_PREFIX = (("claude", "anthropic"), ("gpt", "openai"), ("o1", "openai"), ("o3", "openai"),
              ("o4", "openai"), ("gemini", "gemini"))


#: OpenAI-compatible gateways that resell another vendor's models, as
#: `name -> (base url, the environment variable holding the key)`.
#:
#: A gateway is a transport, not a vendor. The model name, the request shape and the
#: schema are unchanged, so a run that reaches a model through one is still a run of
#: that model -- which is what makes it a usable fallback when a direct account is
#: unavailable mid-batch. It is still worth recording which calls went through it.
GATEWAYS = {"openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY")}


def provider_via(gateway: str) -> Provider:
    """A provider that reaches models through an OpenAI-compatible gateway."""
    if gateway not in GATEWAYS:
        raise LLMError(f"{gateway!r} is not a gateway; known gateways are {sorted(GATEWAYS)}")
    base_url, key_variable = GATEWAYS[gateway]
    key = os.environ.get(key_variable)
    if not key:
        raise LLMError(f"the {gateway} gateway needs {key_variable} in the environment")
    return __getattr__("OpenAIProvider")(api_key=key, base_url=base_url)


def provider_for(model: str) -> Provider:
    """The provider that serves this model name, constructed with its own defaults.

    Naming a model is enough to switch vendors, which is what the comparison
    across models needs: one call site, three models, no branch on vendor.
    """
    name = model.rsplit("/", 1)[-1].lower()      # gateway prefixes such as `openai/gpt-5`
    for prefix, vendor in _BY_PREFIX:
        if name.startswith(prefix):
            return VENDORS[vendor]()
    raise LLMError(f"no provider claims the model {model!r}; known prefixes are "
                   f"{[p for p, _ in _BY_PREFIX]}. Pass `provider=` to name one directly")


def __getattr__(name: str):
    """Import a vendor's module only when it is asked for.

    Each provider needs its vendor's SDK installed. Importing all three eagerly
    would make the package unusable with one of them missing, and the common case
    is that only one is.
    """
    if name in _CLASSES:
        module, cls = _CLASSES[name]
        return getattr(__import__(f"{__package__}.{module}", fromlist=[cls]), cls)
    raise AttributeError(name)


_CLASSES = {"AnthropicProvider": ("anthropic", "AnthropicProvider"),
            "OpenAIProvider": ("openai", "OpenAIProvider"),
            "GeminiProvider": ("gemini", "GeminiProvider")}

VENDORS = {"anthropic": lambda: __getattr__("AnthropicProvider")(),
           "openai": lambda: __getattr__("OpenAIProvider")(),
           "gemini": lambda: __getattr__("GeminiProvider")()}

__all__ = ["Provider", "AnthropicProvider", "OpenAIProvider", "GeminiProvider",
           "DEFAULT_MODEL", "Effort", "EFFORTS", "GATEWAYS", "check_strict", "map_effort",
           "provider_for", "provider_via"]

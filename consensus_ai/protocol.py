"""Protocol definitions for consensus-ai backends.

Uses ``typing.Protocol`` with ``@runtime_checkable`` for structural
subtyping -- no inheritance or ABC required.  All I/O methods are async.
Nothing outside the standard library is imported.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterator, Protocol, runtime_checkable

if TYPE_CHECKING:
    from consensus_ai.types import ChatMessage, ChatResponse


@runtime_checkable
class LLMBackend(Protocol):
    """Provider-agnostic chat completion interface.

    Multi-model consensus is handled by
    :class:`~consensus_ai.consensus_strategies.ConsensusEngine`, which
    wraps any ``LLMBackend`` instance.
    """

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """Send a chat completion request."""
        ...

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Stream content deltas."""
        ...

    async def list_models(self) -> list[str]:
        """Return available model identifiers."""
        ...


@runtime_checkable
class ModelRouter(Protocol):
    """Provider-aware routing with fallback, health checks, and cost estimation."""

    async def route(self, model: str, *, fallback: bool = True) -> LLMBackend:
        """Resolve *model* to an ``LLMBackend``, falling back if unavailable."""
        ...

    async def register_provider(
        self,
        name: str,
        backend: LLMBackend,
        *,
        models: list[str],
        priority: int = 0,
    ) -> None:
        """Register a provider backend with its supported models."""
        ...

    async def list_available_models(self) -> list[Any]:
        """Return metadata for all currently reachable models."""
        ...

    async def provider_health(self) -> dict[str, Any]:
        """Return per-provider health information."""
        ...

    async def estimate_cost(self, model: str, tokens: int) -> float:
        """Return the estimated cost in USD for *tokens* on *model*."""
        ...

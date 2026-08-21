"""Convenience decorators for consensus-ai (ADR-0006: Cross-Cutting Decorators).

Provides ``@with_consensus`` and ``@with_cascade`` decorators that wrap
async LLM call functions with multi-model consensus or cascade fallback
patterns.

Users must explicitly opt in by applying the decorator and configuring
the strategy (ADR-0001: Explicit Opt-In).
"""

from __future__ import annotations

import asyncio
import functools
from typing import Any, Callable

from consensus_ai.consensus_strategies import (
    MajorityVoteStrategy,
    QualityThresholdStrategy,
    ResponseConsensusStrategy,
    WeightedConsensusStrategy,
)
from consensus_ai.patterns import CascadePattern, ConsensusPattern
from consensus_ai.types import ChatResponse, PatternResult


def with_consensus(
    *,
    strategy: str = "majority_vote",
    models: list[str] | int = 3,
    min_quality: float = 0.3,
    weights: dict[str, float] | None = None,
) -> Callable:
    """Decorator that wraps an async LLM call with multi-model consensus.

    The decorated function must accept ``model: str`` as a keyword
    argument and return a ``ChatResponse``.

    Parameters
    ----------
    strategy:
        One of ``"majority_vote"``, ``"weighted"``, or
        ``"quality_threshold"``.
    models:
        Either a list of model identifiers to fan out to, or an integer
        specifying how many times to call the same model (default 3).
    min_quality:
        Minimum quality threshold (only used with
        ``"quality_threshold"`` strategy).
    weights:
        Per-model weights (only used with ``"weighted"`` strategy).

    Returns
    -------
    The decorated function returns a ``ConsensusOutcome`` instead of a
    single ``ChatResponse``.
    """
    strategies: dict[str, Any] = {
        "majority_vote": MajorityVoteStrategy,
        "weighted": lambda: WeightedConsensusStrategy(weights=weights),
        "quality_threshold": lambda: QualityThresholdStrategy(min_quality=min_quality),
    }

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Resolve model list.
            if isinstance(models, int):
                base_model = kwargs.get("model", "default")
                model_list = [base_model] * models
            else:
                model_list = list(models)

            # Fan out model calls concurrently.
            async def _call(model_id: str) -> ChatResponse:
                kw = {**kwargs, "model": model_id}
                return await fn(*args, **kw)

            responses: list[ChatResponse] = list(
                await asyncio.gather(*[_call(m) for m in model_list])
            )

            # Apply consensus strategy.
            if strategy == "majority_vote":
                strat = MajorityVoteStrategy()
            elif strategy == "weighted":
                strat = WeightedConsensusStrategy(weights=weights)
            elif strategy == "quality_threshold":
                strat = QualityThresholdStrategy(min_quality=min_quality)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            return strat.select(responses)

        return wrapper

    return decorator


def with_cascade(
    *,
    fallbacks: list[str],
) -> Callable:
    """Decorator that wraps an async LLM call with cascade fallback.

    The decorated function must accept ``model: str`` as a keyword
    argument and return a ``ChatResponse``.  Models in *fallbacks* are
    tried in order; the first successful response is returned.

    Parameters
    ----------
    fallbacks:
        Ordered list of model identifiers to try.

    Returns
    -------
    The decorated function returns the first successful ``ChatResponse``,
    or raises the last exception if all models fail.
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> ChatResponse:
            errors: list[Exception] = []
            for model_id in fallbacks:
                try:
                    kw = {**kwargs, "model": model_id}
                    return await fn(*args, **kw)
                except Exception as exc:
                    errors.append(exc)

            if errors:
                raise errors[-1]
            raise ValueError("No fallback models provided")

        return wrapper

    return decorator

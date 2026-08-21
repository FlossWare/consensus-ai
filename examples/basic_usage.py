#!/usr/bin/env python3
"""Basic consensus-ai usage: multi-model voting and cascade fallback."""
from __future__ import annotations

import asyncio
from typing import Protocol, runtime_checkable

from consensus_ai import (
    ChatMessage,
    ChatResponse,
    ConsensusPattern,
    CascadePattern,
    MajorityVoteStrategy,
    WeightedConsensusStrategy,
    ConsensusCache,
)


@runtime_checkable
class LLMBackend(Protocol):
    async def chat(
        self, messages: list[ChatMessage], model: str, **kwargs
    ) -> ChatResponse: ...


class MockBackend:
    """Example backend for demonstration. Replace with your real LLM backend."""

    async def chat(
        self, messages: list[ChatMessage], model: str, **kwargs
    ) -> ChatResponse:
        content = f"[{model}] Response to: {messages[-1].content[:50]}"
        return ChatResponse(
            content=content,
            model=model,
            usage={"prompt_tokens": 10, "completion_tokens": 20},
        )


async def main():
    backend = MockBackend()
    models = ["model-a", "model-b", "model-c"]

    # 1. Majority vote consensus
    pattern = ConsensusPattern(
        backend=backend,
        models=models,
        strategy=MajorityVoteStrategy(),
    )
    result = await pattern.execute("What is the best programming language?")
    print(f"Consensus result: {result.response.content}")

    # 2. Weighted consensus (trust model-a more)
    weighted = ConsensusPattern(
        backend=backend,
        models=models,
        strategy=WeightedConsensusStrategy(
            weights={"model-a": 3.0, "model-b": 1.0, "model-c": 1.0}
        ),
    )
    result = await weighted.execute("Explain recursion")
    print(f"Weighted result: {result.response.content}")

    # 3. Cascade fallback (try models in order)
    cascade = CascadePattern(backend=backend, models=models)
    result = await cascade.execute("Generate a haiku")
    print(f"Cascade result: {result.response.content}")

    # 4. Caching
    cache = ConsensusCache(max_size=100)
    print(f"Cache created with max_size=100, current size: {len(cache)}")


if __name__ == "__main__":
    asyncio.run(main())

"""Tests for the consensus-ai package."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from consensus_ai import (
    CascadePattern,
    ChatMessage,
    ChatResponse,
    ConsensusCache,
    ConsensusOutcome,
    ConsensusPattern,
    DisagreementDetector,
    DisagreementReport,
    MajorityVoteStrategy,
    MapReducePattern,
    PatternResult,
    QualityThresholdStrategy,
    WeightedConsensusStrategy,
    with_cascade,
    with_consensus,
)


# -- Helpers -----------------------------------------------------------------


def _make_responses(*contents: str) -> list[ChatResponse]:
    """Build ChatResponse objects from content strings."""
    return [
        ChatResponse(content=c, model=f"model-{i}")
        for i, c in enumerate(contents)
    ]


def _make_backend(response_content: str = "ok") -> AsyncMock:
    """Create a mock LLMBackend that returns a fixed response."""
    backend = AsyncMock()
    backend.chat = AsyncMock(
        return_value=ChatResponse(content=response_content, model="mock")
    )
    return backend


# -- ChatMessage & ChatResponse tests ----------------------------------------


class TestTypes:
    def test_chat_message_fields(self):
        msg = ChatMessage(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"

    def test_chat_response_defaults(self):
        resp = ChatResponse(content="answer")
        assert resp.content == "answer"
        assert resp.model == ""
        assert resp.provider == ""
        assert resp.usage == {}

    def test_pattern_result_defaults(self):
        pr = PatternResult(pattern="test")
        assert pr.pattern == "test"
        assert pr.results == []
        assert pr.metadata == {}
        assert pr.duration_ms == 0.0


# -- MajorityVoteStrategy tests ----------------------------------------------


class TestMajorityVoteStrategy:
    def test_empty_raises(self):
        strategy = MajorityVoteStrategy()
        with pytest.raises(ValueError, match="zero responses"):
            strategy.select([])

    def test_single_response(self):
        strategy = MajorityVoteStrategy()
        responses = _make_responses("hello world")
        outcome = strategy.select(responses)
        assert outcome.selected.content == "hello world"
        assert outcome.strategy == "majority_vote"
        assert outcome.scores == [1.0]

    def test_majority_wins(self):
        strategy = MajorityVoteStrategy()
        responses = _make_responses(
            "the answer is 42",
            "the answer is 42",
            "something completely different",
        )
        outcome = strategy.select(responses)
        # The two identical responses should have higher similarity to each other.
        assert "42" in outcome.selected.content

    def test_scores_length_matches(self):
        strategy = MajorityVoteStrategy()
        responses = _make_responses("a b c", "a b d", "x y z")
        outcome = strategy.select(responses)
        assert len(outcome.scores) == 3


# -- WeightedConsensusStrategy tests ------------------------------------------


class TestWeightedConsensusStrategy:
    def test_empty_raises(self):
        strategy = WeightedConsensusStrategy()
        with pytest.raises(ValueError, match="zero responses"):
            strategy.select([])

    def test_weighted_selection(self):
        strategy = WeightedConsensusStrategy(
            weights={"model-0": 1.0, "model-1": 10.0}
        )
        responses = _make_responses("low weight", "high weight")
        outcome = strategy.select(responses)
        assert outcome.selected.content == "high weight"
        assert outcome.strategy == "weighted"

    def test_default_weight(self):
        strategy = WeightedConsensusStrategy(
            weights={"model-0": 5.0}, default_weight=1.0
        )
        responses = _make_responses("weighted", "default")
        outcome = strategy.select(responses)
        assert outcome.selected.content == "weighted"


# -- QualityThresholdStrategy tests -------------------------------------------


class TestQualityThresholdStrategy:
    def test_empty_raises(self):
        strategy = QualityThresholdStrategy()
        with pytest.raises(ValueError, match="zero responses"):
            strategy.select([])

    def test_invalid_min_quality(self):
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            QualityThresholdStrategy(min_quality=1.5)

    def test_single_response(self):
        strategy = QualityThresholdStrategy(min_quality=0.5)
        responses = _make_responses("only one")
        outcome = strategy.select(responses)
        assert outcome.selected.content == "only one"
        assert outcome.strategy == "quality_threshold"

    def test_fallback_when_all_below_threshold(self):
        strategy = QualityThresholdStrategy(min_quality=0.99)
        responses = _make_responses(
            "completely unique alpha",
            "totally different beta",
            "nothing similar gamma",
        )
        outcome = strategy.select(responses)
        # Should still return something (fallback).
        assert outcome.selected is not None
        assert outcome.metadata.get("fallback") is True


# -- DisagreementDetector tests -----------------------------------------------


class TestDisagreementDetector:
    def test_single_response_no_disagreement(self):
        detector = DisagreementDetector(threshold=0.5)
        responses = _make_responses("hello")
        report = detector.analyze(responses)
        assert report.is_disagreement is False
        assert report.average_similarity == 1.0

    def test_identical_no_disagreement(self):
        detector = DisagreementDetector(threshold=0.5)
        responses = _make_responses("same text", "same text")
        report = detector.analyze(responses)
        assert report.is_disagreement is False
        assert report.average_similarity == 1.0

    def test_divergent_responses_flagged(self):
        detector = DisagreementDetector(threshold=0.5)
        responses = _make_responses(
            "alpha bravo charlie",
            "delta echo foxtrot",
        )
        report = detector.analyze(responses)
        assert report.is_disagreement is True
        assert report.average_similarity < 0.5

    def test_invalid_threshold(self):
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            DisagreementDetector(threshold=-0.1)

    def test_pairwise_scores_populated(self):
        detector = DisagreementDetector()
        responses = _make_responses("a b", "b c", "c d")
        report = detector.analyze(responses)
        # 3 responses -> 3 pairs
        assert len(report.pairwise_scores) == 3


# -- ConsensusCache tests ----------------------------------------------------


class TestConsensusCache:
    def test_put_and_get(self):
        cache = ConsensusCache(max_size=10, ttl_seconds=60)
        outcome = ConsensusOutcome(
            selected=ChatResponse(content="cached"),
            strategy="test",
        )
        cache.put("key1", outcome)
        result = cache.get("key1")
        assert result is not None
        assert result.selected.content == "cached"

    def test_miss_returns_none(self):
        cache = ConsensusCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiry(self):
        cache = ConsensusCache(max_size=10, ttl_seconds=0.01)
        outcome = ConsensusOutcome(
            selected=ChatResponse(content="expires"),
            strategy="test",
        )
        cache.put("key", outcome)
        time.sleep(0.02)
        assert cache.get("key") is None

    def test_lru_eviction(self):
        cache = ConsensusCache(max_size=2, ttl_seconds=60)
        for i in range(3):
            outcome = ConsensusOutcome(
                selected=ChatResponse(content=f"item-{i}"),
                strategy="test",
            )
            cache.put(f"key-{i}", outcome)
        # key-0 should have been evicted.
        assert cache.get("key-0") is None
        assert cache.get("key-1") is not None
        assert cache.get("key-2") is not None

    def test_hash_prompt_deterministic(self):
        h1 = ConsensusCache.hash_prompt("hello", ["a", "b"])
        h2 = ConsensusCache.hash_prompt("hello", ["b", "a"])
        assert h1 == h2  # Models are sorted.

    def test_clear(self):
        cache = ConsensusCache(max_size=10, ttl_seconds=60)
        outcome = ConsensusOutcome(
            selected=ChatResponse(content="data"),
            strategy="test",
        )
        cache.put("k", outcome)
        assert len(cache) == 1
        cache.clear()
        assert len(cache) == 0

    def test_update_existing_key(self):
        cache = ConsensusCache(max_size=10, ttl_seconds=60)
        outcome1 = ConsensusOutcome(
            selected=ChatResponse(content="v1"), strategy="test"
        )
        outcome2 = ConsensusOutcome(
            selected=ChatResponse(content="v2"), strategy="test"
        )
        cache.put("k", outcome1)
        cache.put("k", outcome2)
        assert len(cache) == 1
        assert cache.get("k").selected.content == "v2"


# -- Execution patterns tests ------------------------------------------------


class TestConsensusPattern:
    def test_missing_backend_raises(self):
        pattern = ConsensusPattern()
        with pytest.raises(ValueError, match="backend must be provided"):
            asyncio.run(pattern.execute("task", models=["m1"]))

    def test_consensus_with_backend(self):
        backend = _make_backend("the answer")
        pattern = ConsensusPattern()
        result = asyncio.run(
            pattern.execute("what?", models=["m1", "m2"], backend=backend)
        )
        assert result.pattern == "consensus"
        assert result.metadata["consensus"] == "the answer"
        assert result.metadata["succeeded"] == 2
        assert result.metadata["failed"] == 0

    def test_consensus_handles_errors(self):
        backend = AsyncMock()
        backend.chat = AsyncMock(side_effect=RuntimeError("boom"))
        pattern = ConsensusPattern()
        result = asyncio.run(
            pattern.execute("task", models=["m1"], backend=backend)
        )
        assert result.metadata["failed"] == 1
        assert result.metadata["succeeded"] == 0


class TestCascadePattern:
    def test_cascade_first_success(self):
        backend = _make_backend("first try")
        pattern = CascadePattern()
        result = asyncio.run(
            pattern.execute("task", models=["m1", "m2"], backend=backend)
        )
        assert result.pattern == "cascade"
        assert result.metadata["model_used"] == "m1"
        assert result.metadata["attempts"] == 1

    def test_cascade_fallback_on_error(self):
        call_count = 0

        async def chat_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("first model failed")
            return ChatResponse(content="fallback worked", model="m2")

        backend = AsyncMock()
        backend.chat = AsyncMock(side_effect=chat_side_effect)
        pattern = CascadePattern()
        result = asyncio.run(
            pattern.execute("task", models=["m1", "m2"], backend=backend)
        )
        assert result.metadata["model_used"] == "m2"
        assert result.metadata["attempts"] == 2

    def test_cascade_all_fail(self):
        backend = AsyncMock()
        backend.chat = AsyncMock(side_effect=RuntimeError("fail"))
        pattern = CascadePattern()
        result = asyncio.run(
            pattern.execute("task", models=["m1", "m2"], backend=backend)
        )
        assert result.metadata["model_used"] is None
        assert result.results == []


class TestMapReducePattern:
    def test_map_reduce_combines(self):
        backend = _make_backend("part")
        pattern = MapReducePattern()
        result = asyncio.run(
            pattern.execute("task", models=["m1", "m2"], backend=backend)
        )
        assert result.pattern == "map_reduce"
        assert result.metadata["combined"] == "part\n---\npart"
        assert result.metadata["succeeded"] == 2

    def test_map_reduce_custom_prompt(self):
        backend = _make_backend("mapped")
        pattern = MapReducePattern()
        result = asyncio.run(
            pattern.execute(
                "task",
                models=["m1"],
                backend=backend,
                config={"map_prompt": "custom prompt"},
            )
        )
        assert result.metadata["succeeded"] == 1
        # Verify the custom prompt was used.
        call_args = backend.chat.call_args
        msg = call_args[0][0][0]
        assert msg.content == "custom prompt"


# -- Decorator tests ---------------------------------------------------------


class TestWithConsensusDecorator:
    def test_majority_vote_decorator(self):
        call_log: list[str] = []

        @with_consensus(
            strategy="majority_vote",
            models=["model-a", "model-b", "model-c"],
        )
        async def fake_llm(prompt, *, model="default"):
            call_log.append(model)
            return ChatResponse(content="consensus answer", model=model)

        outcome = asyncio.run(fake_llm("test prompt"))
        assert len(call_log) == 3
        assert set(call_log) == {"model-a", "model-b", "model-c"}
        assert outcome.selected.content == "consensus answer"
        assert outcome.strategy == "majority_vote"

    def test_weighted_decorator(self):
        @with_consensus(
            strategy="weighted",
            models=["low", "high"],
            weights={"low": 1.0, "high": 10.0},
        )
        async def fake_llm(prompt, *, model="default"):
            return ChatResponse(content=f"from {model}", model=model)

        outcome = asyncio.run(fake_llm("test"))
        assert outcome.selected.model == "high"

    def test_integer_models_repeats_call(self):
        call_count = 0

        @with_consensus(strategy="majority_vote", models=3)
        async def fake_llm(prompt, *, model="default"):
            nonlocal call_count
            call_count += 1
            return ChatResponse(content="same", model=model)

        outcome = asyncio.run(fake_llm("test"))
        assert call_count == 3

    def test_unknown_strategy_raises(self):
        @with_consensus(strategy="nonexistent", models=["a"])
        async def fake_llm(prompt, *, model="default"):
            return ChatResponse(content="x", model=model)

        with pytest.raises(ValueError, match="Unknown strategy"):
            asyncio.run(fake_llm("test"))


class TestWithCascadeDecorator:
    def test_cascade_first_succeeds(self):
        @with_cascade(fallbacks=["model-a", "model-b"])
        async def fake_llm(prompt, *, model="default"):
            return ChatResponse(content="ok", model=model)

        result = asyncio.run(fake_llm("test"))
        assert result.model == "model-a"

    def test_cascade_falls_back(self):
        call_count = 0

        @with_cascade(fallbacks=["model-a", "model-b"])
        async def fake_llm(prompt, *, model="default"):
            nonlocal call_count
            call_count += 1
            if model == "model-a":
                raise RuntimeError("model-a down")
            return ChatResponse(content="fallback", model=model)

        result = asyncio.run(fake_llm("test"))
        assert result.model == "model-b"
        assert call_count == 2

    def test_cascade_all_fail_raises(self):
        @with_cascade(fallbacks=["a", "b"])
        async def fake_llm(prompt, *, model="default"):
            raise RuntimeError(f"{model} failed")

        with pytest.raises(RuntimeError, match="b failed"):
            asyncio.run(fake_llm("test"))

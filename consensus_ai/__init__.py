"""consensus-ai: Multi-model consensus strategies and execution patterns.

Provides pluggable strategies for combining responses from multiple LLM
models into a single consensus result, along with execution patterns for
fan-out, cascade, and map-reduce workflows.
"""

from __future__ import annotations

from consensus_ai.consensus_strategies import (
    ConsensusCache,
    ConsensusOutcome,
    DisagreementDetector,
    DisagreementReport,
    MajorityVoteStrategy,
    QualityThresholdStrategy,
    ResponseConsensusStrategy,
    WeightedConsensusStrategy,
)
from consensus_ai.decorators import (
    with_cascade,
    with_consensus,
)
from consensus_ai.patterns import (
    CascadePattern,
    ConsensusPattern,
    MapReducePattern,
)
from consensus_ai.protocol import (
    LLMBackend,
    ModelRouter,
)
from consensus_ai.types import (
    ChatMessage,
    ChatResponse,
    PatternResult,
)

__all__ = [
    # Types
    "ChatMessage",
    "ChatResponse",
    "PatternResult",
    # Protocols
    "LLMBackend",
    "ModelRouter",
    "ResponseConsensusStrategy",
    # Consensus strategies
    "ConsensusOutcome",
    "DisagreementDetector",
    "DisagreementReport",
    "MajorityVoteStrategy",
    "WeightedConsensusStrategy",
    "QualityThresholdStrategy",
    "ConsensusCache",
    # Execution patterns
    "ConsensusPattern",
    "CascadePattern",
    "MapReducePattern",
    # Decorators (ADR-0006)
    "with_consensus",
    "with_cascade",
]

__version__ = "0.1"

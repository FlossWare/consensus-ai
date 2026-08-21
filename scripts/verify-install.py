#!/usr/bin/env python3
"""Verify consensus-ai installation and run a quick smoke test."""
import asyncio
import sys


def main():
    try:
        from consensus_ai import (
            ChatMessage,
            ChatResponse,
            CascadePattern,
            ConsensusCache,
            ConsensusPattern,
            LLMBackend,
            MajorityVoteStrategy,
            MapReducePattern,
            ModelRouter,
            PatternResult,
            QualityThresholdStrategy,
            WeightedConsensusStrategy,
            with_cascade,
            with_consensus,
        )
    except ImportError as e:
        print(f"FAIL: Could not import consensus_ai: {e}")
        print("Install: pip install 'git+https://github.com/FlossWare/consensus-ai.git'")
        sys.exit(1)

    import consensus_ai

    print(f"consensus-ai v{consensus_ai.__version__} installed successfully")
    print(f"Exports: {len(consensus_ai.__all__)} public symbols")

    # Smoke test: strategy instantiation
    strategy = MajorityVoteStrategy()
    print(f"Smoke test: MajorityVoteStrategy created: {strategy}")

    weighted = WeightedConsensusStrategy(
        weights={"model-a": 2.0, "model-b": 1.0}
    )
    print(f"Smoke test: WeightedConsensusStrategy created: {weighted}")

    threshold = QualityThresholdStrategy(threshold=0.7)
    print(f"Smoke test: QualityThresholdStrategy created: {threshold}")

    # Smoke test: cache
    cache = ConsensusCache(max_size=100)
    print(f"Smoke test: ConsensusCache created with max_size=100")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()

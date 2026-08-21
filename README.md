# consensus-ai

Multi-model consensus strategies and execution patterns for LLM orchestration.

Zero external dependencies -- uses only the Python standard library.

## Install

```bash
pip install consensus-ai
```

Or install from source:

```bash
git clone https://github.com/FlossWare/consensus-ai.git
cd consensus-ai
pip install .
```

## Quickstart

```python
from consensus_ai import (
    ChatResponse,
    MajorityVoteStrategy,
    DisagreementDetector,
    ConsensusCache,
)

# Build responses from multiple models
responses = [
    ChatResponse(content="Python is great", model="model-a"),
    ChatResponse(content="Python is great", model="model-b"),
    ChatResponse(content="Rust is great", model="model-c"),
]

# Pick the majority answer
strategy = MajorityVoteStrategy()
outcome = strategy.select(responses)
print(outcome.selected.content)  # "Python is great"

# Detect disagreement
detector = DisagreementDetector(threshold=0.5)
report = detector.analyze(responses)
print(report.is_disagreement)  # True or False

# Cache consensus results
cache = ConsensusCache(max_size=128, ttl_seconds=60)
key = cache.hash_prompt("What is Python?", ["model-a", "model-b"])
cache.put(key, outcome)
cached = cache.get(key)
```

## API Overview

### Types

| Class | Description |
|---|---|
| `ChatMessage` | A single message with `role` and `content` |
| `ChatResponse` | LLM response with `content`, `model`, `provider`, `usage` |
| `PatternResult` | Result from an execution pattern run |

### Protocols

| Protocol | Description |
|---|---|
| `LLMBackend` | Provider-agnostic chat completion interface |
| `ModelRouter` | Provider-aware model routing with fallback |
| `ResponseConsensusStrategy` | Protocol for consensus strategy implementations |

### Consensus Strategies

| Class | Description |
|---|---|
| `MajorityVoteStrategy` | Picks the response most similar to the majority (Jaccard similarity) |
| `WeightedConsensusStrategy` | Selects using per-model weight scores |
| `QualityThresholdStrategy` | Filters below a quality threshold, then selects the best |

### Extras

| Class | Description |
|---|---|
| `DisagreementDetector` | Flags when model responses diverge significantly |
| `ConsensusCache` | Thread-safe LRU cache for consensus results |
| `ConsensusOutcome` | Dataclass holding the selected response, strategy name, and scores |
| `DisagreementReport` | Dataclass summarizing disagreement analysis |

### Execution Patterns

| Class | Description |
|---|---|
| `ConsensusPattern` | Fan-out to all models in parallel, surface the most common answer |
| `CascadePattern` | Try models sequentially, return the first success |
| `MapReducePattern` | Distribute across models in parallel, combine results |

### Decorators (ADR-0006)

| Decorator | Description |
|---|---|
| `@with_consensus(strategy, models)` | Wraps an async LLM call with multi-model consensus |
| `@with_cascade(fallbacks)` | Wraps an async LLM call with cascade fallback |

```python
from consensus_ai import with_consensus, with_cascade

@with_consensus(strategy="majority_vote", models=["gpt-4", "claude", "gemini"])
async def ask(prompt, *, model="default"):
    # Your LLM call here -- will be called once per model
    ...

@with_cascade(fallbacks=["gpt-4", "claude", "gemini"])
async def ask_resilient(prompt, *, model="default"):
    # Tries each model in order until one succeeds
    ...
```

## FlossWare Engineering Standards

This package implements several FlossWare Engineering Standards ADRs:

- **ADR-0001 (Explicit Opt-In)**: Strategies are never activated automatically
- **ADR-0006 (Cross-Cutting Decorators)**: `@with_consensus` and `@with_cascade` decorators
- **ADR-0008 (Free-First)**: Zero external dependencies (stdlib only)
- **ADR-0009 (Core Principles)**: Modular, composable, contracts over implementations
- **ADR-0012 (Multi-Model Consensus Quality Gates)**: This package is the primary implementation
- **ADR-0017 (Agent-Neutral)**: Works with any agent runtime
- **ADR-0020 (Capability-Protocol Separation)**: Transport-independent protocols

See [STANDARDS.md](STANDARDS.md) for full compliance details.

## License

MIT

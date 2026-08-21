# FlossWare Engineering Standards Compliance

This document describes how consensus-ai conforms to the FlossWare Engineering Standards architecture decision records (ADRs).

## ADR Compliance Matrix

| ADR | Title | Status | Notes |
|-----|-------|--------|-------|
| ADR-0001 | Explicit Opt-In | Compliant | Strategies are never activated automatically; users explicitly instantiate and configure them |
| ADR-0006 | Cross-Cutting Decorators | Compliant | `@with_consensus` and `@with_cascade` decorators in `consensus_ai.decorators` |
| ADR-0008 | Free-First | Compliant | Zero external dependencies; stdlib only |
| ADR-0009 | Core Principles | Compliant | Modular, composable; protocols over implementations |
| ADR-0012 | Multi-Model Consensus Quality Gates | **Primary Implementation** | This package implements the quality gates described in ADR-0012 |
| ADR-0017 | Agent-Neutral | Compliant | No agent runtime coupling; works with any framework |
| ADR-0020 | Capability-Protocol Separation | Compliant | All capabilities are transport-independent protocols |

## ADR-0001: Explicit Opt-In

Consensus strategies are never activated automatically. Users must:

1. Import the specific strategy class they want to use
2. Instantiate it with explicit configuration
3. Call `.select()` with their responses

```python
from consensus_ai import MajorityVoteStrategy

strategy = MajorityVoteStrategy()  # Explicit instantiation
outcome = strategy.select(responses)  # Explicit invocation
```

There is no global default, no auto-detection, and no implicit behavior.

## ADR-0006: Cross-Cutting Decorators

The `consensus_ai.decorators` module provides two convenience decorators:

```python
from consensus_ai.decorators import with_consensus, with_cascade

@with_consensus(strategy="majority_vote", models=["gpt-4", "claude", "gemini"])
async def my_llm_call(prompt, *, model="default"):
    ...

@with_cascade(fallbacks=["gpt-4", "claude", "gemini"])
async def my_resilient_call(prompt, *, model="default"):
    ...
```

Both decorators are explicit opt-in (ADR-0001) and require configuration parameters.

## ADR-0008: Free-First

This package has zero external dependencies. All functionality uses only the Python standard library (`dataclasses`, `asyncio`, `hashlib`, `threading`, `collections`, `typing`).

## ADR-0009: Core Principles

- **Modular**: Each strategy is a standalone class; patterns are independent of strategies
- **Composable**: Strategies, detectors, and caches can be combined freely
- **Contracts over implementations**: `ResponseConsensusStrategy`, `LLMBackend`, and `ModelRouter` are `typing.Protocol` definitions, not abstract base classes

## ADR-0012: Multi-Model Consensus Quality Gates

**This package is the primary implementation of ADR-0012.** The three quality gate strategies are:

| Strategy | Purpose | ADR-0012 Gate |
|----------|---------|---------------|
| `MajorityVoteStrategy` | Select the response most models agree on | Agreement gate |
| `WeightedConsensusStrategy` | Score by model reliability weights | Authority gate |
| `QualityThresholdStrategy` | Filter low-quality before selection | Minimum quality gate |

Supporting components:

- `DisagreementDetector` -- quantifies inter-model divergence to flag unreliable consensus
- `ConsensusCache` -- avoids redundant consensus rounds for identical prompts

## ADR-0017: Agent-Neutral

No coupling to any specific agent runtime (LangChain, AutoGen, CrewAI, etc.). The package exposes plain Python protocols and dataclasses that any agent framework can consume.

## ADR-0020: Capability-Protocol Separation

All external interfaces are `typing.Protocol` definitions:

- `LLMBackend` -- chat completion capability (transport-independent)
- `ModelRouter` -- model resolution capability (transport-independent)
- `ResponseConsensusStrategy` -- consensus selection capability

Implementations can use HTTP, gRPC, in-process calls, or any other transport without changing the consensus logic.

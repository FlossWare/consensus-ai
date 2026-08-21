# consensus-ai Integrations

Install from GitHub:

```bash
pip install "git+https://github.com/FlossWare/consensus-ai.git"
```

---

## Claude Code

### CLAUDE.md Snippet

```markdown
## Multi-Model Consensus

This project uses `consensus-ai` for multi-model consensus and cascade fallback.

- Multi-model voting: `from consensus_ai import with_consensus, MajorityVoteStrategy`
- Cascade fallback: `from consensus_ai import with_cascade, CascadePattern`
- Use `@with_consensus` decorator for automatic multi-model fan-out and voting
- Use `@with_cascade` decorator for automatic fallback across providers
- Supports majority vote, weighted consensus, and quality threshold strategies
```

### Hook Example

Create `.claude/hooks/pre-commit.py` to require consensus on important changes:

```python
#!/usr/bin/env python3
"""Pre-commit hook: verify critical changes via multi-model consensus."""
import asyncio
import sys

from consensus_ai import MajorityVoteStrategy, ConsensusPattern


async def verify_change(diff: str, backend, models: list[str]):
    pattern = ConsensusPattern(
        backend=backend,
        models=models,
        strategy=MajorityVoteStrategy(),
    )
    result = await pattern.execute(
        f"Is this code change safe to commit? Reply SAFE or UNSAFE.\n\n{diff}"
    )
    return "UNSAFE" not in result.response.content.upper()


# Usage: pass your backend and model list
# safe = asyncio.run(verify_change(diff, backend, ["gpt-4o", "claude-sonnet", "gemini-flash"]))
```

### Skill Example

Create `.claude/skills/consensus-check.md`:

```markdown
---
name: consensus-check
description: Get multi-model consensus on a question
---

Use consensus-ai to get agreement across multiple models:

\```python
import asyncio
from consensus_ai import ConsensusPattern, MajorityVoteStrategy

async def consensus(question: str, backend, models: list[str]):
    pattern = ConsensusPattern(
        backend=backend,
        models=models,
        strategy=MajorityVoteStrategy(),
    )
    result = await pattern.execute(question)
    return result.response.content

# result = asyncio.run(consensus("Is X correct?", backend, models))
\```
```

---

## OpenAI Codex

### AGENTS.md Snippet

```markdown
## Multi-Model Consensus

Use consensus-ai for decisions requiring agreement across models:
- Install: `pip install "git+https://github.com/FlossWare/consensus-ai.git"`
- Fan-out: `ConsensusPattern(backend, models, strategy)`
- Cascade: `CascadePattern(backend, models)` for fallback
- Strategies: MajorityVote, WeightedConsensus, QualityThreshold
```

### Tool Definition

```python
from consensus_ai import ConsensusPattern, CascadePattern, MajorityVoteStrategy

# Multi-model voting
pattern = ConsensusPattern(
    backend=my_backend,
    models=["gpt-4o", "claude-sonnet", "gemini-flash"],
    strategy=MajorityVoteStrategy(),
)
result = await pattern.execute("Analyze this code for bugs")

# Cascade fallback
cascade = CascadePattern(
    backend=my_backend,
    models=["gpt-4o", "claude-sonnet", "gemini-flash"],  # tried in order
)
result = await cascade.execute("Generate a summary")
```

---

## Cursor

### .cursorrules Snippet

```
When making important decisions or generating critical code, use consensus-ai:

- Import: from consensus_ai import ConsensusPattern, CascadePattern, with_consensus, with_cascade
- Fan out to multiple models: ConsensusPattern(backend, models, strategy)
- Cascade fallback: CascadePattern(backend, models)
- Decorator: @with_consensus(strategy="majority_vote", models=["m1", "m2", "m3"])
- Decorator: @with_cascade(fallbacks=["m1", "m2", "m3"])
- Zero dependencies - stdlib only
- Install: pip install "git+https://github.com/FlossWare/consensus-ai.git"
```

---

## Crush

### Configuration

```python
# crush.config.py
from consensus_ai import ConsensusPattern, CascadePattern, MajorityVoteStrategy

async def consensus_query(question: str, backend, models: list[str]):
    """Get multi-model consensus on a question."""
    pattern = ConsensusPattern(
        backend=backend,
        models=models,
        strategy=MajorityVoteStrategy(),
    )
    return await pattern.execute(question)

async def cascade_query(question: str, backend, models: list[str]):
    """Try models in order until one succeeds."""
    cascade = CascadePattern(backend=backend, models=models)
    return await cascade.execute(question)
```

---

## Generic Python Agent

### Basic asyncio Integration

```python
import asyncio
from consensus_ai import (
    ConsensusPattern,
    CascadePattern,
    MapReducePattern,
    MajorityVoteStrategy,
    WeightedConsensusStrategy,
)

async def main():
    # Majority vote across 3 models
    pattern = ConsensusPattern(
        backend=my_backend,
        models=["model-a", "model-b", "model-c"],
        strategy=MajorityVoteStrategy(),
    )
    result = await pattern.execute("What is 2+2?")
    print(f"Consensus: {result.response.content}")
    print(f"Agreement: {result.metadata.get('agreement', 'N/A')}")

    # Weighted consensus (trust some models more)
    weighted = ConsensusPattern(
        backend=my_backend,
        models=["model-a", "model-b", "model-c"],
        strategy=WeightedConsensusStrategy(
            weights={"model-a": 2.0, "model-b": 1.0, "model-c": 1.0}
        ),
    )

    # Map-reduce for parallel processing
    mr = MapReducePattern(backend=my_backend, models=["m1", "m2", "m3"])
    result = await mr.execute("Analyze this codebase for security issues")

asyncio.run(main())
```

### Decorator Patterns

```python
from consensus_ai import with_consensus, with_cascade

@with_consensus(strategy="majority_vote", models=["m1", "m2", "m3"])
async def review_code(prompt: str, *, model: str = "default") -> ChatResponse:
    return await backend.chat([ChatMessage(role="user", content=prompt)], model=model)

@with_cascade(fallbacks=["gpt-4o", "claude-sonnet", "gemini-flash"])
async def generate(prompt: str, *, model: str = "default") -> ChatResponse:
    return await backend.chat([ChatMessage(role="user", content=prompt)], model=model)
```

---

## Cross-Package Integration

### consensus-ai + resilience-ai

Resilient multi-model consensus with retry and circuit breakers:

```python
from consensus_ai import with_consensus
from resilience_ai import with_retry, with_circuit_breaker

@with_consensus(strategy="majority_vote", models=["m1", "m2", "m3"])
@with_retry(max_attempts=3, backoff=1.0)
@with_circuit_breaker(provider="llm", max_failures=5)
async def reliable_consensus(prompt: str, *, model: str = "default"):
    return await backend.chat([ChatMessage(role="user", content=prompt)], model=model)
```

### consensus-ai + evaluation-ai

Consensus output verified by adversarial panel:

```python
from consensus_ai import with_consensus
from evaluation_ai import adversarial_verify

@adversarial_verify(backend=eval_backend, available_models=["m4", "m5"], panel_size=3)
@with_consensus(strategy="majority_vote", models=["m1", "m2", "m3"])
async def verified_consensus(prompt: str, *, model: str = "default"):
    return await backend.chat([ChatMessage(role="user", content=prompt)], model=model)
```

### Recommended Decorator Stack Order

```python
@track_execution(telemetry=t)      # outermost: track total time
@adversarial_verify(backend=b)     # verify the consensus result
@with_consensus(models=models)     # fan out to multiple models
@with_retry(max_attempts=3)        # retry individual model calls
@with_circuit_breaker(provider=p)  # circuit break per provider
async def robust_query(prompt, *, model="default"):
    ...
```

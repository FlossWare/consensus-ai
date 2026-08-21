#!/bin/bash
# Add consensus-ai integration to your CLAUDE.md
set -e

CLAUDE_MD="${CLAUDE_MD:-./CLAUDE.md}"

if [ ! -f "$CLAUDE_MD" ]; then
    echo "Creating $CLAUDE_MD"
    touch "$CLAUDE_MD"
fi

cat >> "$CLAUDE_MD" << 'EOF'

## Multi-Model Consensus (consensus-ai)

This project uses [consensus-ai](https://github.com/FlossWare/consensus-ai) for multi-model consensus and cascade fallback.

**Install:** `pip install "git+https://github.com/FlossWare/consensus-ai.git"`

**Key imports:**
```python
from consensus_ai import ConsensusPattern, CascadePattern, MajorityVoteStrategy, with_consensus, with_cascade
```

**Usage patterns:**
- Fan-out consensus: `ConsensusPattern(backend, models, MajorityVoteStrategy())`
- Cascade fallback: `CascadePattern(backend, models)`
- Decorator: `@with_consensus(strategy="majority_vote", models=["m1", "m2", "m3"])`
- Decorator: `@with_cascade(fallbacks=["m1", "m2", "m3"])`
- Zero external dependencies (stdlib only)
EOF

echo "Added consensus-ai integration to $CLAUDE_MD"

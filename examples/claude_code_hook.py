#!/usr/bin/env python3
"""Claude Code hook: require multi-model consensus before committing.

Usage as a pre-commit hook in .claude/hooks/pre-commit.py:
    python3 examples/claude_code_hook.py "$DIFF"
"""
from __future__ import annotations

import sys

from consensus_ai import MajorityVoteStrategy


def main():
    if len(sys.argv) < 2:
        print("Usage: claude_code_hook.py <diff_text>")
        sys.exit(1)

    diff_text = sys.argv[1]

    if len(diff_text) < 50:
        print("[consensus-ai] Diff too small to review, skipping")
        sys.exit(0)

    strategy = MajorityVoteStrategy()
    print(f"[consensus-ai] Strategy: {strategy}")
    print(f"[consensus-ai] Diff size: {len(diff_text):,} chars")
    print("[consensus-ai] To run full consensus, provide an LLMBackend and call:")
    print("  pattern = ConsensusPattern(backend, models, MajorityVoteStrategy())")
    print('  result = await pattern.execute(f"Review this diff: {diff}")')


if __name__ == "__main__":
    main()

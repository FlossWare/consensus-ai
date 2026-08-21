"""Core data types for consensus-ai.

All types are plain dataclasses with no imports outside the standard
library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    """A single message in an LLM chat conversation."""

    role: str
    content: str


@dataclass
class ChatResponse:
    """Response from an LLM chat completion request."""

    content: str
    model: str = ""
    provider: str = ""
    usage: dict = field(default_factory=dict)


@dataclass
class PatternResult:
    """Result from an execution pattern run.

    Attributes
    ----------
    pattern:
        Name of the execution pattern (e.g. ``"consensus"``,
        ``"cascade"``, ``"map_reduce"``).
    results:
        Per-model result dicts produced during execution.
    metadata:
        Pattern-specific summary data (e.g. consensus answer,
        combined output, error list).
    duration_ms:
        Wall-clock execution time in milliseconds.
    """

    pattern: str
    results: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    duration_ms: float = 0.0

"""Pure data types for the package — no PolicyEngine imports allowed here."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Reform:
    """A homepage prompt paired with the PolicyEngine reform that backs it.

    ``swap=True`` flips the displayed winner / loser percentages. Use this when
    the prompt asks "who benefits from <existing policy>" but the simulated
    reform is the *repeal* of that policy. Households that lose under the
    repeal are the households that benefit from current law.
    """

    key: str
    text: str
    reform: dict[str, dict[str, Any]] = field(default_factory=dict)
    swap: bool = False

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("key must be non-empty")
        if not self.text:
            raise ValueError("text must be non-empty")
        if not self.reform:
            raise ValueError(
                "reform dict must contain at least one parameter override; "
                "an empty reform produces no winners or losers"
            )


@dataclass(frozen=True)
class ImpactResult:
    """Output of running one reform against the baseline microsimulation."""

    key: str
    text: str
    share_gain: float
    share_lose: float
    total_change: float
    mean_change: float
    swap: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.share_gain <= 1.0:
            raise ValueError(f"share_gain must be in [0, 1], got {self.share_gain}")
        if not 0.0 <= self.share_lose <= 1.0:
            raise ValueError(f"share_lose must be in [0, 1], got {self.share_lose}")

    @property
    def winner_pct(self) -> float:
        """Share of households the prompt frames as gaining."""
        return self.share_lose if self.swap else self.share_gain

    @property
    def loser_pct(self) -> float:
        """Share of households the prompt frames as losing."""
        return self.share_gain if self.swap else self.share_lose

    def to_prompt_dict(self) -> dict[str, Any]:
        """Shape consumed by the homepage ``PromptData`` interface."""
        return {
            "text": self.text,
            "winnerPct": self.winner_pct,
            "loserPct": self.loser_pct,
        }

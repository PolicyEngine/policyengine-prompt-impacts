"""Registry of homepage prompts paired with PolicyEngine reforms."""

from __future__ import annotations

from policyengine_prompt_impacts.domain import Reform
from policyengine_prompt_impacts.reforms import uk, us

__all__ = ["all_reforms", "uk", "us"]


def all_reforms() -> dict[str, Reform]:
    """Return every registered reform keyed by ``Reform.key``."""
    return {r.key: r for r in [*uk.REFORMS, *us.REFORMS]}

"""Output formatters: JSON for tooling, TSX array literal for the website."""

from __future__ import annotations

import json
from collections.abc import Iterable

from policyengine_prompt_impacts.domain import ImpactResult


def emit_json(results: Iterable[ImpactResult]) -> str:
    """Serialize a list of results as a JSON object keyed by ``Reform.key``."""
    return json.dumps(
        {
            r.key: {
                "text": r.text,
                "share_gain": r.share_gain,
                "share_lose": r.share_lose,
                "total_change": r.total_change,
                "mean_change": r.mean_change,
                "swap": r.swap,
                "winner_pct": r.winner_pct,
                "loser_pct": r.loser_pct,
            }
            for r in results
        },
        indent=2,
        ensure_ascii=False,
    )


# Floor below which a share is treated as simulation noise rather than a
# real distributional finding. Set just under the smallest "real" share we
# want to surface (the no-tax-on-tips prompt is ~0.4% of households).
NOISE_FLOOR = 0.002


def _format_pct(value: float) -> str:
    """Format a percentage for the homepage TS file.

    Sub-2% values keep three decimal places — the no-tax-on-tips deduction
    benefits ~0.4% of households and rounding that to 0% would erase the
    finding. Anything below ``NOISE_FLOOR`` rounds to 0 to avoid
    surfacing simulation noise (e.g. trace state-tax interactions in a
    federal-only reform).
    """
    if value < NOISE_FLOOR:
        return "0"
    rounded = round(value, 3 if value < 0.01 else 2)
    # Drop trailing zeros and the trailing dot
    text = f"{rounded:.3f}".rstrip("0").rstrip(".")
    return text or "0"


def emit_tsx_prompt_list(results: Iterable[ImpactResult]) -> str:
    """Produce the array literal for ``TypewriterPrompt.tsx``.

    The output is paste-ready; the caller still owns surrounding context
    (the ``const UK_PROMPTS: PromptData[] =`` declaration and the trailing
    semicolon).
    """
    items = []
    for r in results:
        # Quote the text as a JS/TS string literal but keep non-ASCII chars
        # (£, €) literal so the rendered prompt matches the source.
        text_literal = json.dumps(r.text, ensure_ascii=False)
        items.append(
            "  {\n"
            f"    text: {text_literal},\n"
            f"    winnerPct: {_format_pct(r.winner_pct)},\n"
            f"    loserPct: {_format_pct(r.loser_pct)},\n"
            "  }"
        )
    return "[\n" + ",\n".join(items) + ",\n]"

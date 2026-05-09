"""Output emitter tests — JSON and TSX-prompts-array generators."""

from __future__ import annotations

import json

from policyengine_prompt_impacts.domain import ImpactResult
from policyengine_prompt_impacts.emit import emit_json, emit_tsx_prompt_list


def make_result(**overrides) -> ImpactResult:
    base = {
        "key": "demo",
        "text": "the impact of demo",
        "share_gain": 0.30,
        "share_lose": 0.10,
        "total_change": 1e9,
        "mean_change": 100.0,
        "swap": False,
    }
    base.update(overrides)
    return ImpactResult(**base)


def test_emit_json_round_trip() -> None:
    results = [make_result(), make_result(key="other", swap=True)]
    out = emit_json(results)
    parsed = json.loads(out)
    assert set(parsed.keys()) == {"demo", "other"}
    assert parsed["demo"]["share_gain"] == 0.30
    assert parsed["other"]["swap"] is True


def test_emit_tsx_prompt_list_basic_shape() -> None:
    results = [
        make_result(text="how raising X affects Y", share_gain=0.4, share_lose=0.0),
    ]
    out = emit_tsx_prompt_list(results)
    # Must be valid TSX/TS array literal — caller can paste straight into
    # TypewriterPrompt.tsx.
    assert out.startswith("[")
    assert out.rstrip().endswith("]")
    assert '"how raising X affects Y"' in out
    assert "winnerPct: 0.4" in out
    assert "loserPct: 0" in out


def test_emit_tsx_prompt_list_respects_swap() -> None:
    results = [
        make_result(
            text="who benefits from the no-tax-on-tips deduction",
            share_gain=0.0,
            share_lose=0.13,
            swap=True,
        )
    ]
    out = emit_tsx_prompt_list(results)
    assert "winnerPct: 0.13" in out
    assert "loserPct: 0" in out


def test_emit_tsx_prompt_list_rounds_to_two_decimals() -> None:
    results = [
        make_result(share_gain=0.6159, share_lose=0.0004),
    ]
    out = emit_tsx_prompt_list(results)
    # Two-decimal rounding by default
    assert "winnerPct: 0.62" in out
    assert "loserPct: 0" in out


def test_emit_tsx_prompt_list_three_decimal_precision_for_micro_shares() -> None:
    """Sub-1% shares (tipped-worker prompt is 0.4%) need finer precision so
    they don't all collapse to 0."""
    results = [
        make_result(share_gain=0.00355, share_lose=0.0),
    ]
    out = emit_tsx_prompt_list(results)
    # 0.00355 rounds to 0.004 at 3-decimal precision
    assert "winnerPct: 0.004" in out


def test_emit_tsx_prompt_list_floors_simulation_noise_to_zero() -> None:
    """Sub-0.2% shares are below the visualization's resolution AND below
    PolicyEngine's typical sim noise (state-tax interactions, rounding in
    the survey weights). They should display as 0, not a fake-precision
    0.001."""
    results = [
        # share_lose 0.001 (0.1%) is sim noise from a state-tax interaction
        make_result(share_gain=0.14, share_lose=0.0011),
    ]
    out = emit_tsx_prompt_list(results)
    assert "winnerPct: 0.14" in out
    assert "loserPct: 0," in out


def test_emit_tsx_prompt_list_keeps_real_signal_above_noise_floor() -> None:
    """The 0.4% tipped-worker prompt is real signal and must not be
    floored. The noise floor is set just below this value."""
    results = [make_result(share_gain=0.004, share_lose=0.0)]
    out = emit_tsx_prompt_list(results)
    assert "winnerPct: 0.004" in out


def test_emit_tsx_prompt_list_keeps_non_ascii_literals() -> None:
    """£ and other non-ASCII characters must round-trip as themselves; if the
    emitter escapes them to \\uXXXX the prompt still renders, but the diff is
    much harder to review and matches the homepage source verbatim."""
    results = [
        make_result(text="the cost of doubling child benefit at £25/week"),
    ]
    out = emit_tsx_prompt_list(results)
    assert "£25/week" in out
    assert "\\u00a3" not in out

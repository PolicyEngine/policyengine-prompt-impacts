"""Tests for domain types: Reform, ImpactResult."""

from __future__ import annotations

import pytest

from policyengine_prompt_impacts.domain import ImpactResult, Reform


def test_reform_minimal_construction() -> None:
    reform = Reform(
        key="us_demo",
        text="how a demo reform behaves",
        reform={
            "gov.irs.credits.ctc.amount.base[0].amount": {"2026-01-01.2100-12-31": 3000}
        },
    )
    assert reform.key == "us_demo"
    assert reform.swap is False


def test_reform_swap_default_is_false() -> None:
    reform = Reform(key="k", text="t", reform={"p": {"2026-01-01.2100-12-31": 1}})
    assert reform.swap is False


def test_reform_key_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="key must be non-empty"):
        Reform(key="", text="t", reform={})


def test_reform_text_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="text must be non-empty"):
        Reform(key="k", text="", reform={})


def test_reform_reform_dict_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="reform dict must contain"):
        Reform(key="k", text="t", reform={})


# ---- ImpactResult: winner_pct / loser_pct depend on swap ----


def test_impact_result_no_swap_passes_through() -> None:
    r = ImpactResult(
        key="k",
        text="t",
        share_gain=0.4,
        share_lose=0.1,
        total_change=1e9,
        mean_change=100.0,
        swap=False,
    )
    assert r.winner_pct == 0.4
    assert r.loser_pct == 0.1


def test_impact_result_swap_flips_gain_and_lose() -> None:
    """When swap=True, the prompt asks 'who benefits from X' but the simulated
    reform is the *repeal* of X. Losers under the simulated reform are the
    winners under current law (which is what we display).
    """
    r = ImpactResult(
        key="k",
        text="t",
        share_gain=0.0,
        share_lose=0.13,
        total_change=-1e9,
        mean_change=-100.0,
        swap=True,
    )
    assert r.winner_pct == 0.13
    assert r.loser_pct == 0.0


def test_impact_result_shares_clamped_in_zero_one() -> None:
    with pytest.raises(ValueError, match="share_gain must be in"):
        ImpactResult(
            key="k",
            text="t",
            share_gain=1.5,
            share_lose=0.0,
            total_change=0.0,
            mean_change=0.0,
        )
    with pytest.raises(ValueError, match="share_lose must be in"):
        ImpactResult(
            key="k",
            text="t",
            share_gain=0.0,
            share_lose=-0.1,
            total_change=0.0,
            mean_change=0.0,
        )


def test_impact_result_to_prompt_dict() -> None:
    r = ImpactResult(
        key="k",
        text="who benefits from doubling X",
        share_gain=0.0,
        share_lose=0.13,
        total_change=-1e9,
        mean_change=-100.0,
        swap=True,
    )
    assert r.to_prompt_dict() == {
        "text": "who benefits from doubling X",
        "winnerPct": 0.13,
        "loserPct": 0.0,
    }

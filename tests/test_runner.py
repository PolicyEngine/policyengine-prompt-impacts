"""Runner tests with a fake Microsimulation — no actual PolicyEngine sim."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pytest

from policyengine_prompt_impacts.domain import Reform
from policyengine_prompt_impacts.runner import ImpactRunner


class FakeMicroSeries:
    """Minimal stand-in for microdf.MicroSeries.

    Holds parallel arrays of values and weights and returns weighted shares
    via .mean() / .sum() — enough to drive the runner's branch logic.
    """

    def __init__(self, values: Sequence[float], weights: Sequence[float]) -> None:
        if len(values) != len(weights):
            raise AssertionError("values and weights must align")
        self._values = list(values)
        self._weights = list(weights)

    def __sub__(self, other: FakeMicroSeries) -> FakeMicroSeries:
        diffs = [a - b for a, b in zip(self._values, other._values, strict=True)]
        return FakeMicroSeries(diffs, self._weights)

    def __gt__(self, threshold: float) -> FakeMicroSeries:
        bools = [1.0 if v > threshold else 0.0 for v in self._values]
        return FakeMicroSeries(bools, self._weights)

    def __lt__(self, threshold: float) -> FakeMicroSeries:
        bools = [1.0 if v < threshold else 0.0 for v in self._values]
        return FakeMicroSeries(bools, self._weights)

    def mean(self) -> float:
        wsum = sum(self._weights)
        if wsum == 0:
            return 0.0
        return (
            sum(v * w for v, w in zip(self._values, self._weights, strict=True)) / wsum
        )

    def sum(self) -> float:
        return sum(v * w for v, w in zip(self._values, self._weights, strict=True))


class FakeMicrosim:
    """Returns a programmable household_net_income series."""

    def __init__(self, series: FakeMicroSeries) -> None:
        self._series = series

    def calc(self, variable: str, period: int) -> FakeMicroSeries:
        assert variable == "household_net_income"
        return self._series

    # Used by the UK code path:
    def calculate(self, variable: str, period: int) -> FakeMicroSeries:
        return self.calc(variable, period)


def make_factory(
    base_values: Sequence[float],
    reform_values: Sequence[float],
    weights: Sequence[float],
):
    """Return a factory that yields baseline first, then reformed."""
    calls: list[dict[str, Any]] = []

    def factory(reform: dict | None = None):
        calls.append({"reform": reform})
        if reform is None:
            return FakeMicrosim(FakeMicroSeries(base_values, weights))
        return FakeMicrosim(FakeMicroSeries(reform_values, weights))

    factory.calls = calls  # type: ignore[attr-defined]
    return factory


# ---- Tests ----


def test_runner_computes_winner_and_loser_shares() -> None:
    # Six households, equal weights: 3 gain, 2 lose, 1 unchanged
    factory = make_factory(
        base_values=[100, 100, 100, 100, 100, 100],
        reform_values=[200, 150, 110, 100, 50, 0],
        weights=[1, 1, 1, 1, 1, 1],
    )
    runner = ImpactRunner(microsim_factory=factory, year=2026)
    reform = Reform(key="test", text="t", reform={"path": {"2026-01-01.2100-12-31": 1}})
    result = runner.run(reform)
    assert result.share_gain == pytest.approx(3 / 6)
    assert result.share_lose == pytest.approx(2 / 6)
    # diffs are [+100, +50, +10, 0, -50, -100] → sum = +10
    assert result.total_change == pytest.approx(10)
    assert result.mean_change == pytest.approx(10 / 6)
    assert result.swap is False


def test_runner_uses_unit_threshold_for_gain_lose() -> None:
    """Tiny rounding noise (sub-currency-unit) should not register as a change."""
    factory = make_factory(
        base_values=[100, 100, 100],
        reform_values=[100.5, 100.0, 99.5],  # +0.5, 0, -0.5
        weights=[1, 1, 1],
    )
    runner = ImpactRunner(microsim_factory=factory, year=2026)
    reform = Reform(key="test", text="t", reform={"p": {"2026-01-01.2100-12-31": 1}})
    result = runner.run(reform)
    # Sub-unit changes are filtered out, so 0% gain and 0% lose
    assert result.share_gain == 0.0
    assert result.share_lose == 0.0


def test_runner_passes_reform_dict_to_factory() -> None:
    factory = make_factory(
        base_values=[0],
        reform_values=[0],
        weights=[1],
    )
    runner = ImpactRunner(microsim_factory=factory, year=2026)
    reform_dict = {"gov.something": {"2026-01-01.2100-12-31": 99}}
    runner.run(Reform(key="k", text="t", reform=reform_dict))
    # 1st call = baseline (None), 2nd call = reformed
    assert factory.calls == [
        {"reform": None},
        {"reform": reform_dict},
    ]


def test_runner_propagates_swap_flag() -> None:
    factory = make_factory(
        base_values=[0, 0],
        reform_values=[1, 0],
        weights=[1, 1],
    )
    runner = ImpactRunner(microsim_factory=factory, year=2026)
    result = runner.run(
        Reform(
            key="k",
            text="t",
            reform={"p": {"2026-01-01.2100-12-31": 1}},
            swap=True,
        )
    )
    assert result.swap is True


def test_runner_uses_household_weight_via_microseries_mean() -> None:
    """The runner relies on MicroSeries weighting — never on raw counts.

    Two households, weight 1 and 9. Household 0 gains 100; household 1
    unchanged. Weighted share_gain should be 1/(1+9) = 0.10, not 0.50.
    """
    factory = make_factory(
        base_values=[0, 0],
        reform_values=[100, 0],
        weights=[1, 9],
    )
    runner = ImpactRunner(microsim_factory=factory, year=2026)
    result = runner.run(
        Reform(key="k", text="t", reform={"p": {"2026-01-01.2100-12-31": 1}})
    )
    assert result.share_gain == pytest.approx(0.10)

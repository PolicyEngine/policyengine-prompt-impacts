"""Run one PolicyEngine reform and return its distributional summary."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from policyengine_prompt_impacts.domain import ImpactResult, Reform

# Households whose net income shifts by less than this absolute amount are
# treated as unaffected. PolicyEngine occasionally reports rounding noise
# in the cents, so a $1 / £1 floor avoids spurious "winners".
DEFAULT_THRESHOLD = 1.0


class _MicroSimLike(Protocol):
    """Minimal protocol the runner needs from a Microsimulation object.

    PolicyEngine-US exposes ``calc()``; PolicyEngine-UK exposes
    ``calculate()``. Either is fine — the runner picks whichever exists.
    """

    def calc(self, variable: str, period: int) -> Any: ...  # pragma: no cover

    def calculate(self, variable: str, period: int) -> Any: ...  # pragma: no cover


MicrosimFactory = Callable[..., _MicroSimLike]


def _calculate(microsim: _MicroSimLike, variable: str, period: int) -> Any:
    """Call ``calc`` on US sims, ``calculate`` on UK sims."""
    if hasattr(microsim, "calc"):
        return microsim.calc(variable, period)
    return microsim.calculate(variable, period)


class ImpactRunner:
    """Compute share-gain / share-lose / cost for one reform.

    Parameters
    ----------
    microsim_factory:
        Callable that returns a Microsimulation. Called with no arguments for
        the baseline and with ``reform=...`` for the reformed run. Use
        ``policyengine_us.Microsimulation`` or ``policyengine_uk.Microsimulation``
        directly, or wrap them to inject a dataset path.
    year:
        Calendar year to evaluate (default 2026 — the PolicyEngine prompt
        baseline year).
    threshold:
        Absolute change in household net income below which a household is
        considered unaffected.
    """

    def __init__(
        self,
        microsim_factory: MicrosimFactory,
        year: int = 2026,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        self._factory = microsim_factory
        self._year = year
        self._threshold = threshold

    def run(self, reform: Reform) -> ImpactResult:
        baseline = self._factory()
        reformed = self._factory(reform=reform.reform)

        base_inc = _calculate(baseline, "household_net_income", self._year)
        ref_inc = _calculate(reformed, "household_net_income", self._year)
        diff = ref_inc - base_inc

        share_gain = float((diff > self._threshold).mean())
        share_lose = float((diff < -self._threshold).mean())
        total_change = float(diff.sum())
        mean_change = float(diff.mean())

        return ImpactResult(
            key=reform.key,
            text=reform.text,
            share_gain=share_gain,
            share_lose=share_lose,
            total_change=total_change,
            mean_change=mean_change,
            swap=reform.swap,
        )

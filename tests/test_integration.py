"""Integration tests — actually run PolicyEngine.

Each test is marked ``integration`` so the default ``pytest`` invocation
skips them. CI runs them in a separate, slower job. Runtime is dominated
by Microsimulation construction (~30s baseline + ~30s per reform).

Run locally with:

    uv run pytest -m integration
"""

from __future__ import annotations

import pytest

from policyengine_prompt_impacts.cli import _build_uk_runner, _build_us_runner
from policyengine_prompt_impacts.domain import Reform
from policyengine_prompt_impacts.runner import ImpactRunner

pytestmark = pytest.mark.integration


PERIOD = "2026-01-01.2100-12-31"


@pytest.fixture(scope="module")
def uk_runner() -> ImpactRunner:
    """Yield a runner backed by PolicyEngine-UK."""
    pytest.importorskip("policyengine_uk")
    return _build_uk_runner()


@pytest.fixture(scope="module")
def us_runner() -> ImpactRunner:
    """Yield a runner backed by PolicyEngine-US."""
    pytest.importorskip("policyengine_us")
    return _build_us_runner()


@pytest.mark.uk
def test_uk_basic_rate_increase_creates_losers(uk_runner: ImpactRunner) -> None:
    """Raising the basic rate from 20p to 25p should leave most UK
    households worse off and almost no households better off. Exact
    percentages drift with each policyengine-uk-data release; we only
    assert direction and order of magnitude."""
    result = uk_runner.run(
        Reform(
            key="uk_basic_rate_25_test",
            text="raise basic rate to 25p",
            reform={"gov.hmrc.income_tax.rates.uk[0].rate": {PERIOD: 0.25}},
        )
    )
    assert result.share_lose > 0.5
    assert result.share_gain < 0.05
    assert result.total_change < 0  # net cost to households (revenue gain)


@pytest.mark.us
def test_us_triple_standard_deduction_creates_winners(us_runner: ImpactRunner) -> None:
    """Tripling the standard deduction is a tax cut; most filers should
    benefit, almost none should lose."""
    result = us_runner.run(
        Reform(
            key="us_triple_sd_test",
            text="triple standard deduction",
            reform={
                "gov.irs.deductions.standard.amount.SINGLE": {PERIOD: 16_100 * 3},
                "gov.irs.deductions.standard.amount.JOINT": {PERIOD: 32_200 * 3},
                "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
                    PERIOD: 24_150 * 3
                },
                "gov.irs.deductions.standard.amount.SEPARATE": {PERIOD: 16_100 * 3},
                "gov.irs.deductions.standard.amount.SURVIVING_SPOUSE": {
                    PERIOD: 32_200 * 3
                },
            },
        )
    )
    assert result.share_gain > 0.4
    assert result.share_lose < 0.05
    assert result.total_change > 0

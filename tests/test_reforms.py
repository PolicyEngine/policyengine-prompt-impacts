"""Sanity checks on the bundled reform registries."""

from __future__ import annotations

import re

import pytest

from policyengine_prompt_impacts.domain import Reform
from policyengine_prompt_impacts.reforms import all_reforms, uk, us

PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.\d{4}-\d{2}-\d{2}$")


@pytest.mark.parametrize(
    "module,country,expected_count",
    [
        (uk, "uk", 16),
        (us, "us", 15),
    ],
)
def test_country_module_lists_expected_reforms(module, country, expected_count) -> None:
    reforms = module.REFORMS
    assert isinstance(reforms, list)
    assert all(isinstance(r, Reform) for r in reforms)
    assert len(reforms) == expected_count, (
        f"{country.upper()} prompt count drifted; update both the homepage "
        f"and this test together."
    )


def test_keys_are_unique_within_country() -> None:
    for reforms in (uk.REFORMS, us.REFORMS):
        keys = [r.key for r in reforms]
        assert len(keys) == len(set(keys)), f"duplicate key in {keys}"


def test_keys_are_namespaced_by_country() -> None:
    assert all(r.key.startswith("uk_") for r in uk.REFORMS)
    assert all(r.key.startswith("us_") for r in us.REFORMS)


def test_periods_use_yyyy_mm_dd_dot_yyyy_mm_dd_format() -> None:
    for reform in [*uk.REFORMS, *us.REFORMS]:
        for path, period_map in reform.reform.items():
            for period in period_map:
                assert PERIOD_PATTERN.match(period), (
                    f"{reform.key}: parameter {path} has malformed period {period!r}"
                )


def test_all_reforms_returns_combined_dict() -> None:
    combined = all_reforms()
    # Every key from both registries appears
    for r in [*uk.REFORMS, *us.REFORMS]:
        assert r.key in combined
    # No extra entries
    assert len(combined) == len(uk.REFORMS) + len(us.REFORMS)


def test_no_period_starts_in_the_past() -> None:
    """Reforms should activate in the prompt year (2026) or later — never with
    an effective date before then. Catches accidental year typos."""
    for reform in [*uk.REFORMS, *us.REFORMS]:
        for path, period_map in reform.reform.items():
            for period in period_map:
                start_year = int(period.split("-")[0])
                assert start_year >= 2026, (
                    f"{reform.key}: parameter {path} starts in {start_year}; "
                    f"must be 2026 or later to apply to the prompt year"
                )

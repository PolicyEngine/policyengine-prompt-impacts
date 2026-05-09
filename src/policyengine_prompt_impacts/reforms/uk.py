"""UK homepage prompts and their PolicyEngine-UK reform definitions.

Order in this list matches the order shown on the homepage.
"""

from __future__ import annotations

from policyengine_prompt_impacts.domain import Reform

PERIOD = "2026-01-01.2100-12-31"

REFORMS: list[Reform] = [
    Reform(
        key="uk_basic_rate_25",
        text="the impact of raising the basic rate to 25p",
        reform={"gov.hmrc.income_tax.rates.uk[0].rate": {PERIOD: 0.25}},
    ),
    Reform(
        key="uk_child_benefit_40_per_week_universal",
        text="the poverty impact of a £40/week universal child benefit",
        reform={
            "gov.hmrc.child_benefit.amount.eldest": {PERIOD: 40.0},
            "gov.hmrc.child_benefit.amount.additional": {PERIOD: 40.0},
            "gov.hmrc.child_benefit.opt_out_rate": {PERIOD: 0.0},
        },
    ),
    Reform(
        key="uk_abolish_personal_allowance",
        text="who loses from abolishing the personal allowance",
        reform={
            "gov.hmrc.income_tax.allowances.personal_allowance.amount": {PERIOD: 0.0}
        },
    ),
    Reform(
        key="uk_additional_rate_50",
        text="revenue from a 50p additional rate",
        reform={"gov.hmrc.income_tax.rates.uk[2].rate": {PERIOD: 0.50}},
    ),
    Reform(
        key="uk_remove_benefit_cap",
        text="how removing the benefit cap affects single parents",
        reform={
            "gov.dwp.benefit_cap.single.in_london": {PERIOD: 1_000_000.0},
            "gov.dwp.benefit_cap.single.outside_london": {PERIOD: 1_000_000.0},
            "gov.dwp.benefit_cap.non_single.in_london": {PERIOD: 1_000_000.0},
            "gov.dwp.benefit_cap.non_single.outside_london": {PERIOD: 1_000_000.0},
        },
    ),
    Reform(
        key="uk_uc_standard_allowance_cut_10_per_week",
        text="the poverty impact of cutting the UC standard allowance by £10/week",
        # SA values are monthly; £10/wk == 10*52/12 ≈ £43.33/mo. Targets are
        # the 2026 PolicyEngine baselines minus the cut. Verify against
        # `gov.dwp.universal_credit.standard_allowance.amount.{cat}` after a
        # PolicyEngine-UK version bump — uprating will shift the baseline
        # and these absolute targets will silently drift.
        reform={
            "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD": {
                PERIOD: 370.41  # baseline 413.74 - 43.33
            },
            "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG": {
                PERIOD: 284.42  # baseline 327.76 - 43.33
            },
            "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD": {
                PERIOD: 606.12  # baseline 649.46 - 43.33
            },
            "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG": {
                PERIOD: 471.13  # baseline 514.47 - 43.33
            },
        },
    ),
    Reform(
        key="uk_uc_taper_45",
        text="how reducing the UC taper rate to 45% affects workers",
        reform={"gov.dwp.universal_credit.means_test.reduction_rate": {PERIOD: 0.45}},
    ),
    Reform(
        key="uk_state_pension_cut_5pct",
        text="who loses from a 5% cut to the state pension",
        reform={
            "gov.dwp.state_pension.new_state_pension.amount": {PERIOD: 241.3 * 0.95},
            "gov.dwp.state_pension.basic_state_pension.amount": {PERIOD: 184.9 * 0.95},
        },
    ),
    Reform(
        key="uk_ni_threshold_300_per_week",
        text="how raising NI thresholds affects low-income workers",
        reform={
            "gov.hmrc.national_insurance.class_1.thresholds.primary_threshold": {
                PERIOD: 300.0
            }
        },
    ),
    Reform(
        key="uk_uc_work_allowance_double",
        text="who gains from doubling the UC work allowance",
        reform={
            "gov.dwp.universal_credit.means_test.work_allowance.with_housing": {
                PERIOD: 850.0
            },
            "gov.dwp.universal_credit.means_test.work_allowance.without_housing": {
                PERIOD: 1416.0
            },
        },
    ),
    Reform(
        key="uk_child_benefit_plus_25_per_week",
        text="the poverty impact of a £25/week child benefit increase",
        reform={
            "gov.hmrc.child_benefit.amount.eldest": {PERIOD: 51.94},
            "gov.hmrc.child_benefit.amount.additional": {PERIOD: 42.84},
        },
    ),
    Reform(
        key="uk_double_child_benefit",
        text="the cost of doubling child benefit",
        reform={
            "gov.hmrc.child_benefit.amount.eldest": {PERIOD: 26.94 * 2},
            "gov.hmrc.child_benefit.amount.additional": {PERIOD: 17.84 * 2},
        },
    ),
    Reform(
        key="uk_higher_rate_threshold_up",
        text="how raising the higher rate threshold affects middle earners",
        reform={"gov.hmrc.income_tax.rates.uk[1].threshold": {PERIOD: 50_000.0}},
    ),
    Reform(
        key="uk_higher_rate_threshold_down",
        text="who loses from lowering the higher rate threshold to £40,000",
        reform={"gov.hmrc.income_tax.rates.uk[1].threshold": {PERIOD: 27_430.0}},
    ),
    Reform(
        key="uk_double_marriage_allowance",
        text="how doubling the marriage allowance affects couples",
        reform={"gov.hmrc.income_tax.allowances.marriage_allowance.max": {PERIOD: 0.2}},
    ),
    Reform(
        key="uk_lower_additional_rate_threshold",
        text="the impact of lowering the additional rate threshold",
        reform={"gov.hmrc.income_tax.rates.uk[2].threshold": {PERIOD: 100_000.0}},
    ),
]

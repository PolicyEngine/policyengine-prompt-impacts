"""US homepage prompts and their PolicyEngine-US reform definitions.

Order in this list matches the order shown on the homepage.

Several reforms set ``swap=True``: the prompt asks "who benefits from
<existing OBBBA provision>" but the simulated reform is the *repeal* of
that provision. Households that lose under the simulated repeal are the
households that benefit from current law.
"""

from __future__ import annotations

from policyengine_prompt_impacts.domain import Reform

PERIOD = "2026-01-01.2100-12-31"

# Filing-status standard deduction amounts at 2026 (for the "tripling" reform)
SD_SINGLE = 16_100
SD_JOINT = 32_200
SD_HEAD = 24_150
SD_SS = 32_200

REFORMS: list[Reform] = [
    Reform(
        key="us_triple_standard_deduction",
        text="how tripling the standard deduction affects median income",
        reform={
            "gov.irs.deductions.standard.amount.SINGLE": {PERIOD: SD_SINGLE * 3},
            "gov.irs.deductions.standard.amount.JOINT": {PERIOD: SD_JOINT * 3},
            "gov.irs.deductions.standard.amount.HEAD_OF_HOUSEHOLD": {
                PERIOD: SD_HEAD * 3
            },
            "gov.irs.deductions.standard.amount.SEPARATE": {PERIOD: SD_SINGLE * 3},
            "gov.irs.deductions.standard.amount.SURVIVING_SPOUSE": {PERIOD: SD_SS * 3},
        },
    ),
    Reform(
        key="us_expand_ctc_to_3600",
        text="the poverty impact of expanding the Child Tax Credit",
        reform={"gov.irs.credits.ctc.amount.base[0].amount": {PERIOD: 3_600}},
    ),
    Reform(
        key="us_expand_eitc_50pct",
        text="the distributional impact of expanding the EITC",
        reform={
            "gov.irs.credits.eitc.max[0].amount": {PERIOD: 670 * 1.5},
            "gov.irs.credits.eitc.max[1].amount": {PERIOD: 4475 * 1.5},
            "gov.irs.credits.eitc.max[2].amount": {PERIOD: 7393 * 1.5},
            "gov.irs.credits.eitc.max[3].amount": {PERIOD: 8316 * 1.5},
        },
    ),
    Reform(
        key="us_remove_salt_cap",
        text="the impact of removing the SALT cap on high earners",
        reform={
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SINGLE": {
                PERIOD: float("inf")
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.JOINT": {
                PERIOD: float("inf")
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.HEAD_OF_HOUSEHOLD": {
                PERIOD: float("inf")
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SEPARATE": {
                PERIOD: float("inf")
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SURVIVING_SPOUSE": {
                PERIOD: float("inf")
            },
        },
    ),
    Reform(
        key="us_ctc_fully_refundable",
        text="the cost of making the Child Tax Credit fully refundable",
        reform={"gov.irs.credits.ctc.refundable.fully_refundable": {PERIOD: True}},
    ),
    Reform(
        key="us_double_snap",
        text="the poverty impact of doubling SNAP benefits",
        reform={
            f"gov.usda.snap.max_allotment.main.CONTIGUOUS_US.{i}": {PERIOD: v * 2}
            for i, v in [
                (1, 305),
                (2, 559),
                (3, 800),
                (4, 1015),
                (5, 1206),
                (6, 1448),
                (7, 1601),
                (8, 1830),
            ]
        },
    ),
    Reform(
        key="us_raise_all_rates_5pp",
        text="the impact of raising all income tax rates by 5 points",
        reform={
            f"gov.irs.income.bracket.rates.{i}": {PERIOD: r + 0.05}
            for i, r in [
                (1, 0.10),
                (2, 0.12),
                (3, 0.22),
                (4, 0.24),
                (5, 0.32),
                (6, 0.35),
                (7, 0.37),
            ]
        },
    ),
    Reform(
        key="us_eliminate_payroll_cap",
        text="who pays more from eliminating the payroll tax cap",
        reform={"gov.irs.payroll.social_security.cap": {PERIOD: 1e9}},
    ),
    Reform(
        key="us_top_rate_45",
        text="how raising the top rate to 45% affects revenue",
        # PE-US bracket 7 is the 37% bracket (with threshold "inf" — the next
        # rung). Bracket 6 is the operational top in many cases, so bump both.
        reform={
            "gov.irs.income.bracket.rates.6": {PERIOD: 0.43},
            "gov.irs.income.bracket.rates.7": {PERIOD: 0.45},
        },
    ),
    Reform(
        key="us_double_cdcc",
        text="who benefits from doubling the Child and Dependent Care Credit",
        reform={
            "gov.irs.credits.cdcc.max": {PERIOD: 6_000},
            "gov.irs.credits.cdcc.eligibility.max": {PERIOD: 4},
        },
    ),
    Reform(
        key="us_increase_ssi_25pct",
        text="how raising SSI benefits by 25% affects poverty",
        reform={
            "gov.ssa.ssi.amount.individual": {PERIOD: 994 * 1.25},
            "gov.ssa.ssi.amount.couple": {PERIOD: 1491 * 1.25},
        },
    ),
    Reform(
        key="us_lower_salt_cap_10k",
        text="the revenue from lowering the SALT cap to $10,000",
        reform={
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SINGLE": {
                PERIOD: 10_000.0
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.JOINT": {
                PERIOD: 10_000.0
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.HEAD_OF_HOUSEHOLD": {
                PERIOD: 10_000.0
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SEPARATE": {
                PERIOD: 5_000.0
            },
            "gov.irs.deductions.itemized.salt_and_real_estate.cap.SURVIVING_SPOUSE": {
                PERIOD: 10_000.0
            },
        },
    ),
    Reform(
        key="us_arpa_ctc",
        text="the impact of restoring the expanded Child Tax Credit",
        # 2021 ARPA: $3,600 (under 6), $3,000 (6+), fully refundable.
        reform={
            "gov.irs.credits.ctc.amount.arpa[0].amount": {PERIOD: 3_600},
            "gov.irs.credits.ctc.amount.arpa[1].amount": {PERIOD: 3_000},
            "gov.irs.credits.ctc.refundable.fully_refundable": {PERIOD: True},
        },
    ),
    Reform(
        key="us_repeal_senior_bonus",
        text="who benefits from the senior bonus deduction",
        # OBBBA's senior bonus deduction is currently $6,000.
        # Reform = repeal; swap so the prompt reads "who benefits".
        reform={"gov.irs.deductions.senior_deduction.amount": {PERIOD: 0}},
        swap=True,
    ),
    Reform(
        key="us_repeal_tip_deduction",
        text="who benefits from the no-tax-on-tips deduction",
        # OBBBA's tipped income deduction is capped at $25,000.
        # Reform = repeal; swap so the prompt reads "who benefits".
        reform={"gov.irs.deductions.tip_income.cap": {PERIOD: 0.0}},
        swap=True,
    ),
]

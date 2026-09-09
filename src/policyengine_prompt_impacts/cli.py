"""Command-line entry point.

Subcommands:

- ``run`` — run every registered reform against the protected legacy PolicyEngine
  models and emit a JSON results file. Optionally also writes the
  ``UK_PROMPTS`` / ``US_PROMPTS`` array literal for pasting into
  ``TypewriterPrompt.tsx``.
- ``list`` — list registered reforms without running anything.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable
from pathlib import Path

from policyengine_prompt_impacts.domain import ImpactResult, Reform
from policyengine_prompt_impacts.emit import emit_json, emit_tsx_prompt_list
from policyengine_prompt_impacts.reforms import uk, us
from policyengine_prompt_impacts.runner import ImpactRunner
from policyengine_prompt_impacts.runtime import check_runtime, validate_runtime


def _build_uk_runner() -> ImpactRunner:
    validate_runtime("uk")
    # Importing inside the function so that `cli list` works without UK
    # installed (and so the test suite can run without policyengine_uk).
    from policyengine_uk import Microsimulation as UKMicrosim

    dataset = os.environ.get(
        "POLICYENGINE_UK_DEFAULT_DATASET",
        "hf://policyengine/policyengine-uk-data-private/enhanced_frs_2023_24.h5",
    )

    def factory(reform=None):
        if reform is None:
            return UKMicrosim(dataset=dataset)
        return UKMicrosim(dataset=dataset, reform=reform)

    return ImpactRunner(microsim_factory=factory, year=2026)


def _build_us_runner() -> ImpactRunner:
    from policyengine_prompt_impacts.legacy_us import resolve_dataset

    dataset = resolve_dataset()

    from policyengine_core.reforms import Reform as USReform
    from policyengine_us import Microsimulation as USMicrosim

    def factory(reform=None):
        if reform is None:
            return USMicrosim(dataset=dataset)
        return USMicrosim(
            dataset=dataset, reform=USReform.from_dict(reform, "policyengine_us")
        )

    return ImpactRunner(microsim_factory=factory, year=2026)


def _print_results(country: str, reforms: Iterable[Reform]) -> list[ImpactResult]:
    runner = _build_uk_runner() if country == "uk" else _build_us_runner()
    out: list[ImpactResult] = []
    for reform in reforms:
        print(f"-- {reform.key}: {reform.text}", flush=True)
        try:
            result = runner.run(reform)
        except Exception as exc:  # noqa: BLE001 — surface anything informative
            raise RuntimeError(
                f"{country.upper()} reform '{reform.key}' failed: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
        print(
            f"   share_gain={result.share_gain:.3%} "
            f"share_lose={result.share_lose:.3%} "
            f"total={result.total_change / 1e9:+.1f}B",
            flush=True,
        )
        out.append(result)
    return out


def cmd_run(args: argparse.Namespace) -> int:
    if args.country not in ("uk", "us"):
        raise ValueError("Run requires one country: 'uk' or 'us'.")
    countries = {"uk": uk.REFORMS, "us": us.REFORMS}
    selected = [args.country]

    all_results: list[ImpactResult] = []
    try:
        for country in selected:
            all_results.extend(_print_results(country, countries[country]))
    except Exception as exc:  # noqa: BLE001 — CLI must fail before output emission
        print(
            f"ERROR: {type(exc).__name__}: {exc}. No output files were written.",
            file=sys.stderr,
            flush=True,
        )
        return 1

    if args.json:
        Path(args.json).write_text(emit_json(all_results))
        print(f"wrote JSON → {args.json}", flush=True)

    if args.tsx:
        # One TSX block per country — paste into TypewriterPrompt.tsx
        sections: list[str] = []
        for country in selected:
            country_results = [
                r for r in all_results if r.key.startswith(f"{country}_")
            ]
            sections.append(
                f"// === {country.upper()} ===\n"
                f"const {country.upper()}_PROMPTS: PromptData[] = "
                f"{emit_tsx_prompt_list(country_results)};"
            )
        Path(args.tsx).write_text("\n\n".join(sections) + "\n")
        print(f"wrote TSX → {args.tsx}", flush=True)

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    countries = (
        (uk.REFORMS, us.REFORMS)
        if args.country == "all"
        else ((uk.REFORMS,) if args.country == "uk" else (us.REFORMS,))
    )
    payload = {
        r.key: {"text": r.text, "swap": r.swap}
        for reforms in countries
        for r in reforms
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_check_runtime(args: argparse.Namespace) -> int:
    json.dump(check_runtime(args.country), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="policyengine-prompt-impacts",
        description="Compute distributional impacts for the PolicyEngine "
        "homepage typewriter prompts.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run reforms and emit results.")
    run.add_argument("--country", choices=("uk", "us"), required=True)
    run.add_argument("--json", help="Path to write JSON results")
    run.add_argument(
        "--tsx",
        help=(
            "Path to write a paste-ready TSX prompt-array block "
            "for TypewriterPrompt.tsx"
        ),
    )
    run.set_defaults(func=cmd_run)

    listing = sub.add_parser("list", help="List registered reforms.")
    listing.add_argument("--country", choices=("uk", "us", "all"), default="all")
    listing.set_defaults(func=cmd_list)

    runtime = sub.add_parser(
        "check-runtime",
        help="Verify one installed country API without population data.",
    )
    runtime.add_argument("--country", choices=("uk", "us"), required=True)
    runtime.set_defaults(func=cmd_check_runtime)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI smoke tests — only the parsing / list path; ``run`` requires PE."""

from __future__ import annotations

import json
import sys
from types import SimpleNamespace

import pytest

from policyengine_prompt_impacts.cli import build_parser, main


def test_parser_help_does_not_crash() -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])
    assert exc_info.value.code == 0


def test_list_uk_outputs_uk_reforms_only(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["list", "--country", "uk"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert all(k.startswith("uk_") for k in payload)
    assert len(payload) == 16


def test_list_all_includes_both_countries(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["list", "--country", "all"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert any(k.startswith("uk_") for k in payload)
    assert any(k.startswith("us_") for k in payload)
    assert len(payload) == 16 + 15


def test_uk_runner_passes_explicit_dataset_to_both_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from policyengine_prompt_impacts import runtime
    from policyengine_prompt_impacts.cli import _build_uk_runner

    monkeypatch.setattr(
        runtime.metadata, "version", runtime.EXPECTED_PACKAGES["uk"].__getitem__
    )
    calls = []
    dataset = "/existing/private-uk.h5"
    monkeypatch.setenv("POLICYENGINE_UK_DEFAULT_DATASET", dataset)
    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk",
        SimpleNamespace(Microsimulation=lambda **kwargs: calls.append(kwargs)),
    )
    reform = {"parameter": {"2026-01-01.2100-12-31": 1}}
    runner = _build_uk_runner()
    runner._factory()
    runner._factory(reform=reform)
    assert calls == [
        {"dataset": dataset},
        {"dataset": dataset, "reform": reform},
    ]


@pytest.mark.parametrize("arguments", [["run"], ["run", "--country", "all"]])
def test_run_requires_one_explicit_country(arguments: list[str]) -> None:
    """A calculation cannot silently combine incompatible country runtimes."""
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(arguments)
    assert exc_info.value.code == 2

"""CLI parsing and output safety tests without population calculations."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from policyengine_prompt_impacts.cli import build_parser, main
from policyengine_prompt_impacts.domain import ImpactResult, Reform


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
    dataset = "hf://policyengine/private-uk/population.h5@verified-revision"
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


def _result_for(reform: Reform) -> ImpactResult:
    return ImpactResult(
        key=reform.key,
        text=reform.text,
        share_gain=0.25,
        share_lose=0.5,
        total_change=-100,
        mean_change=-10,
        swap=reform.swap,
    )


@pytest.mark.parametrize("country", ["uk", "us"])
@pytest.mark.parametrize("existing_files", [False, True])
@pytest.mark.parametrize(
    "failure_phase",
    ["runner-setup", "simulation-factory", "first-reform", "later-reform"],
)
def test_failed_run_never_writes_outputs(
    country: str,
    existing_files: bool,
    failure_phase: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Constructor and reform errors cannot publish empty or partial results."""
    from policyengine_prompt_impacts import cli
    from policyengine_prompt_impacts.runner import ImpactRunner

    paths = [tmp_path / "results.json", tmp_path / "prompts.tsx"]
    original = b"previous successful output\n"
    if existing_files:
        for path in paths:
            path.write_bytes(original)

    calls = []

    def fail(*args, **kwargs):
        raise RuntimeError("Dataset could not be loaded")

    def run(reform):
        calls.append(reform.key)
        if failure_phase == "first-reform" or len(calls) == 2:
            fail()
        return _result_for(reform)

    def build_runner():
        if failure_phase == "runner-setup":
            fail()
        if failure_phase == "simulation-factory":
            return ImpactRunner(microsim_factory=fail)
        return SimpleNamespace(run=run)

    monkeypatch.setattr(cli, f"_build_{country}_runner", build_runner)
    rc = main(
        ["run", "--country", country, "--json", str(paths[0]), "--tsx", str(paths[1])]
    )

    assert rc != 0
    captured = capsys.readouterr()
    assert "Dataset could not be loaded" in captured.err
    assert "No output files were written" in captured.err
    assert "wrote JSON" not in captured.out
    assert "wrote TSX" not in captured.out
    for path in paths:
        if existing_files:
            assert path.read_bytes() == original
        else:
            assert not path.exists()
    if failure_phase in ("first-reform", "later-reform"):
        assert len(calls) == (1 if failure_phase == "first-reform" else 2)
        assert calls[-1] in captured.err


@pytest.mark.parametrize("country", ["uk", "us"])
def test_successful_run_emits_every_selected_reform(
    country: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from policyengine_prompt_impacts import cli

    monkeypatch.setattr(
        cli, f"_build_{country}_runner", lambda: SimpleNamespace(run=_result_for)
    )
    json_path = tmp_path / "results.json"
    tsx_path = tmp_path / "prompts.tsx"

    rc = main(
        ["run", "--country", country, "--json", str(json_path), "--tsx", str(tsx_path)]
    )

    assert rc == 0
    reforms = getattr(cli, country).REFORMS
    payload = json.loads(json_path.read_text())
    assert list(payload) == [reform.key for reform in reforms]
    tsx = tsx_path.read_text()
    assert f"const {country.upper()}_PROMPTS: PromptData[]" in tsx
    assert tsx.count("winnerPct:") == len(reforms)

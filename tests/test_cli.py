"""CLI smoke tests — only the parsing / list path; ``run`` requires PE."""

from __future__ import annotations

import json

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

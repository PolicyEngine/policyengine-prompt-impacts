"""Protect the legacy model from moving data pointers and incompatible installs."""

from __future__ import annotations

import hashlib
import sys
from types import SimpleNamespace

import pytest

from policyengine_prompt_impacts import legacy_us, runtime


@pytest.fixture
def matching_versions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        runtime.metadata, "version", legacy_us.EXPECTED_PACKAGES.__getitem__
    )


def test_rejects_new_spm_before_downloading(monkeypatch: pytest.MonkeyPatch) -> None:
    versions = {**legacy_us.EXPECTED_PACKAGES, "spm-calculator": "1.0.0"}
    monkeypatch.setattr(runtime.metadata, "version", versions.__getitem__)
    monkeypatch.setitem(sys.modules, "huggingface_hub", None)
    with pytest.raises(RuntimeError, match="spm-calculator.*0.3.1.*1.0.0"):
        legacy_us.resolve_dataset()


def test_download_uses_immutable_commit_and_checks_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path, matching_versions
) -> None:
    path = tmp_path / "populace_us_2024.h5"
    payload = b"test artifact bytes; no population data"
    path.write_bytes(payload)
    monkeypatch.setattr(
        legacy_us, "DATASET_SHA256", hashlib.sha256(payload).hexdigest()
    )
    requests = []

    def download(**kwargs):
        requests.append(kwargs)
        return str(path)

    monkeypatch.setitem(
        sys.modules, "huggingface_hub", SimpleNamespace(hf_hub_download=download)
    )
    assert legacy_us.resolve_dataset() == str(path)
    assert requests == [
        {
            "repo_id": "policyengine/populace-us",
            "repo_type": "dataset",
            "filename": "populace_us_2024.h5",
            "revision": "f09f2f3b9fa8409642dc0c7fc9c8f7516ae0e3c5",
        }
    ]


def test_rejects_changed_dataset_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path, matching_versions
) -> None:
    path = tmp_path / "populace_us_2024.h5"
    path.write_bytes(b"unexpected release")
    monkeypatch.setitem(
        sys.modules,
        "huggingface_hub",
        SimpleNamespace(hf_hub_download=lambda **kwargs: str(path)),
    )
    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        legacy_us.resolve_dataset()


def test_baseline_and_reform_use_the_same_verified_dataset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from policyengine_prompt_impacts.cli import _build_us_runner

    monkeypatch.setattr(legacy_us, "resolve_dataset", lambda: "/verified/build-p.h5")
    calls = []

    def microsimulation(**kwargs):
        calls.append(kwargs)
        return object()

    converted_reform = object()
    monkeypatch.setitem(
        sys.modules, "policyengine_us", SimpleNamespace(Microsimulation=microsimulation)
    )
    monkeypatch.setitem(
        sys.modules,
        "policyengine_core.reforms",
        SimpleNamespace(
            Reform=SimpleNamespace(from_dict=lambda *args: converted_reform)
        ),
    )
    runner = _build_us_runner()
    runner._factory()
    runner._factory(reform={"parameter": {"2026-01-01.2100-12-31": 1}})
    assert calls == [
        {"dataset": "/verified/build-p.h5"},
        {"dataset": "/verified/build-p.h5", "reform": converted_reform},
    ]

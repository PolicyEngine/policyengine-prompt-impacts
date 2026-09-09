"""Wrong country environments fail before model imports or data access."""

import sys
from importlib import metadata

import pytest

from policyengine_prompt_impacts import runtime
from policyengine_prompt_impacts.cli import _build_uk_runner


def test_uk_rejects_us_core_before_country_import(monkeypatch):
    versions = {**runtime.EXPECTED_PACKAGES["uk"], "policyengine-core": "3.26.11"}
    monkeypatch.setattr(runtime.metadata, "version", versions.__getitem__)
    monkeypatch.setitem(sys.modules, "policyengine_uk", None)
    with pytest.raises(RuntimeError, match="policyengine-core==3.26.1.*3.26.11"):
        _build_uk_runner()


def test_missing_country_reports_the_selected_install(monkeypatch):
    def missing(name):
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(runtime.metadata, "version", missing)
    with pytest.raises(RuntimeError, match="--extra uk.*own environment"):
        runtime.check_runtime("uk")


def test_unknown_country_never_falls_back_to_another_model():
    with pytest.raises(ValueError, match="Unsupported country"):
        runtime.check_runtime("all")

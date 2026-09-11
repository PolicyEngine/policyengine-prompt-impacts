"""Country-specific legacy runtime boundaries, without eager model imports."""

from __future__ import annotations

from importlib import import_module, metadata
from typing import Any

EXPECTED_PACKAGES = {
    "us": {
        "policyengine-us": "1.764.6",
        "policyengine-core": "3.26.11",
        "spm-calculator": "0.3.1",
    },
    # Preserve the original UK lock; newer Core rejects this country's variables.
    "uk": {"policyengine-uk": "2.88.13", "policyengine-core": "3.26.1"},
}


def validate_runtime(country: str) -> dict[str, str]:
    """Refuse a wrong environment before importing a country or fetching data."""
    if country not in EXPECTED_PACKAGES:
        raise ValueError(f"Unsupported country: {country!r}; choose 'uk' or 'us'.")
    installed = {}
    for package, expected in EXPECTED_PACKAGES[country].items():
        try:
            version = metadata.version(package)
        except metadata.PackageNotFoundError:
            version = None
        if version != expected:
            raise RuntimeError(
                f"Legacy {country.upper()} runtime requires {package}=={expected}, "
                f"found {version!r}; install with uv sync --locked --extra dev "
                f"--extra {country} in its own environment."
            )
        installed[package] = version
    return installed


def check_runtime(country: str) -> dict[str, Any]:
    """Import the selected real country API without opening a population."""
    packages = validate_runtime(country)
    model = import_module(f"policyengine_{country}")
    return {
        "country": country,
        "packages": packages,
        "microsimulation_class": (
            f"{model.Microsimulation.__module__}.{model.Microsimulation.__qualname__}"
        ),
    }

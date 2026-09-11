"""Explicit legacy US runtime pending the coordinated canonical SPM release."""

from __future__ import annotations

import hashlib
from pathlib import Path

from policyengine_prompt_impacts.runtime import EXPECTED_PACKAGES as RUNTIMES
from policyengine_prompt_impacts.runtime import validate_runtime

# Build P's release_manifest.json certifies this country/Core pair. The old
# country's SPM requirement is unbounded, so SPM must be checked independently.
EXPECTED_PACKAGES = RUNTIMES["us"]
DATASET_RELEASE = "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z"
DATASET_REVISION = "f09f2f3b9fa8409642dc0c7fc9c8f7516ae0e3c5"
DATASET_SHA256 = "48b9d479fb4fd1c3537f9383ce4697d130b6f618658409d74f6233c43b994c7e"


def resolve_dataset() -> str:
    """Return the verified Build P file for the exact installed legacy runtime.

    Download by immutable HF commit, never country defaults, main or latest.json.
    Check both installed packages and artifact bytes before any model imports.
    """
    validate_runtime("us")

    # Lazy import keeps CLI list and the regular unit suite country-independent.
    from huggingface_hub import hf_hub_download

    path = Path(
        hf_hub_download(
            repo_id="policyengine/populace-us",
            repo_type="dataset",
            filename="populace_us_2024.h5",
            revision=DATASET_REVISION,
        )
    )
    with path.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != DATASET_SHA256:
        raise RuntimeError(
            f"Build P dataset SHA-256 mismatch: expected {DATASET_SHA256}, "
            f"found {actual}. Refusing to use a different population."
        )
    return str(path)

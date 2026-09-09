"""Real installed imports in the selected CI environment; no population work."""

import json
import subprocess
import sys

import pytest

from policyengine_prompt_impacts.runtime import EXPECTED_PACKAGES


@pytest.mark.native
@pytest.mark.parametrize(
    "country",
    [
        pytest.param("uk", marks=pytest.mark.uk),
        pytest.param("us", marks=pytest.mark.us),
    ],
)
def test_selected_native_runtime_imports_without_the_other_country(country):
    command = (
        "from policyengine_prompt_impacts.cli import main; "
        f"main(['check-runtime', '--country', '{country}']); "
        "import sys; "
        f"assert 'policyengine_{'us' if country == 'uk' else 'uk'}' not in sys.modules"
    )
    completed = subprocess.run(
        [sys.executable, "-c", command], capture_output=True, text=True, check=True
    )
    result = json.loads(completed.stdout)
    assert result["country"] == country
    assert result["packages"] == EXPECTED_PACKAGES[country]
    assert result["microsimulation_class"].startswith(f"policyengine_{country}.")

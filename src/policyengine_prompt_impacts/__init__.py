"""Compute distributional impacts for the typewriter prompts on the
PolicyEngine homepage.

Public surface:

- ``Reform`` — a homepage prompt paired with a PolicyEngine reform dict.
- ``ImpactResult`` — the computed share-gain / share-lose / cost summary.
- ``ImpactRunner`` — runs a single reform and returns an ``ImpactResult``.
- ``reforms.uk.REFORMS`` / ``reforms.us.REFORMS`` — the registered prompts.
- ``emit.emit_tsx_prompt_list`` — produce the array literal that lives in
  ``website/src/components/home/TypewriterPrompt.tsx``.
"""

from policyengine_prompt_impacts.domain import ImpactResult, Reform
from policyengine_prompt_impacts.emit import emit_json, emit_tsx_prompt_list
from policyengine_prompt_impacts.runner import ImpactRunner

__all__ = [
    "ImpactResult",
    "ImpactRunner",
    "Reform",
    "emit_json",
    "emit_tsx_prompt_list",
]

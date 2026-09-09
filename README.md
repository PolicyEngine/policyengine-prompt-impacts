# policyengine-prompt-impacts

Computes the distributional impact of every typewriter prompt on the
[PolicyEngine homepage](https://policyengine.org), so the winner / loser
percentages displayed on the household-graph visualization come from real
PolicyEngine simulations rather than guesses.

The package owns:

- the **reform definitions** mapping each prompt to a PolicyEngine reform
  (`policyengine_prompt_impacts.reforms.uk.REFORMS`,
  `policyengine_prompt_impacts.reforms.us.REFORMS`);
- a **runner** that executes each reform against the PolicyEngine baseline
  and computes share-gain / share-lose / cost
  (`policyengine_prompt_impacts.ImpactRunner`);
- **emitters** that produce machine-readable JSON or a paste-ready TSX
  array literal for `website/src/components/home/TypewriterPrompt.tsx`
  (`policyengine_prompt_impacts.emit`).

## Usage

The active generator uses separate locked country environments. US uses its
certified US 1.764.6/Core 3.26.11/SPM 0.3.1 tuple. UK retains the project's
original UK 2.88.13/Core 3.26.1 tuple; it cannot initialize with the US Core
version. Both selections are recorded in `uv.lock`. Their extras are mutually
exclusive, and each calculation must explicitly select one country.

```bash
# UK (requires access to the existing private data source)
UV_PROJECT_ENVIRONMENT=.venv-uk uv sync --locked --extra dev --extra uk
uv pip check --python .venv-uk/bin/python
UV_PROJECT_ENVIRONMENT=.venv-uk uv run --no-sync \
  policyengine-prompt-impacts check-runtime --country uk
UV_PROJECT_ENVIRONMENT=.venv-uk uv run --no-sync policyengine-prompt-impacts run --country uk \
  --json uk.json --tsx uk.tsx

# US
UV_PROJECT_ENVIRONMENT=.venv-us uv sync --locked --extra dev --extra us
uv pip check --python .venv-us/bin/python
UV_PROJECT_ENVIRONMENT=.venv-us uv run --no-sync \
  policyengine-prompt-impacts check-runtime --country us
UV_PROJECT_ENVIRONMENT=.venv-us uv run --no-sync policyengine-prompt-impacts run --country us \
  --json us.json --tsx us.tsx

# List every country's reforms without importing either model.
uv run policyengine-prompt-impacts list
```

`check-runtime` validates the installed tuple and imports the real selected
country API without downloading or constructing a population. A `run` without
`--country`, or with `--country all`, is rejected before calculation. To produce
both countries' outputs, run the two commands above in their own environments.

The `--tsx` output is a `UK_PROMPTS` / `US_PROMPTS` array literal ready to
paste into `TypewriterPrompt.tsx` on `policyengine-app-v2`.

US runs explicitly download Build P's `populace_us_2024.h5` from HF commit
`f09f2f3b9fa8409642dc0c7fc9c8f7516ae0e3c5` and verify SHA-256
`48b9d479fb4fd1c3537f9383ce4697d130b6f618658409d74f6233c43b994c7e` before
constructing either simulation. Build P certifies US 1.764.6/Core 3.26.11;
the runtime also checks SPM 0.3.1. It does not follow `main`, `latest.json`,
or the country model's default dataset. A mismatched environment or artifact
fails before population computation.

UK retains the existing private `enhanced_frs_2023_24.h5` source, passed
explicitly to both simulations. `POLICYENGINE_UK_DEFAULT_DATASET` can select
a different existing path. That archived source is still mutable and has
not been certified here; it is outside the Microcosm-US publication gate.

These changes do not regenerate or relabel existing homepage results.
The final canonical generator needs the coordinated published model/data
bundle and returned provenance before new JSON/TSX is generated and the
homepage is updated.

## Development

```bash
uv sync --locked --extra dev      # no country deps — unit tests only
uv run --no-sync pytest           # unit tests (no PolicyEngine sim required)
uv run --no-sync ruff format .
uv run --no-sync ruff check .

# Real country API check, without population work.
UV_PROJECT_ENVIRONMENT=.venv-us uv run --no-sync pytest -m 'native and us'

# Separately authorized population integration; use the matching environment.
UV_PROJECT_ENVIRONMENT=.venv-us uv run --no-sync pytest -m 'integration and us'
UV_PROJECT_ENVIRONMENT=.venv-uk uv run --no-sync pytest -m 'integration and uk'
```

CI runs unit tests plus native API checks in separate country jobs on every push.
The integration workflow also runs separate country jobs; each installs only
its own locked extra and selects only that country's tests. It is opt-in (see
`.github/workflows/integration.yml`) because PolicyEngine simulations take
several minutes and require HuggingFace dataset access. The integration
workflow needs a `POLICYENGINE_HF_TOKEN` repo secret with read access to
the `policyengine/policyengine-uk-data-private` dataset.

## How `swap` works

Some prompts ask "who benefits from `<existing OBBBA provision>`" — the
homepage is asking about the *current law*, so the simulated reform has to
be the *repeal* of that provision and the displayed winner / loser
percentages are flipped. `Reform.swap=True` handles this:

- households that *lose* under the simulated repeal are the households
  that *benefit* from current law — these are shown as `winnerPct`
- households that *gain* under the simulated repeal are the households
  that *lose* from current law — these are shown as `loserPct`

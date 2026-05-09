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

`policyengine-uk` and `policyengine-us` pin different `policyengine-core`
versions and **cannot live in the same virtualenv**. Install one country
at a time, or use two separate venvs:

```bash
# UK
uv venv -p 3.13 .venv-uk
uv pip install -e ".[dev,uk]" --python .venv-uk/bin/python
.venv-uk/bin/policyengine-prompt-impacts run --country uk \
  --json uk.json --tsx uk.tsx

# US (separate venv)
uv venv -p 3.13 .venv-us
uv pip install -e ".[dev,us]" --python .venv-us/bin/python
.venv-us/bin/policyengine-prompt-impacts run --country us \
  --json us.json --tsx us.tsx

# List registered reforms (no PolicyEngine sim required — works in either venv)
policyengine-prompt-impacts list
```

The `--tsx` output is a `UK_PROMPTS` / `US_PROMPTS` array literal ready to
paste into `TypewriterPrompt.tsx` on `policyengine-app-v2`.

## Development

```bash
uv pip install -e ".[dev]"      # no PE country deps — unit tests only
uv run pytest                   # unit tests (no PolicyEngine sim required)
uv run pytest -m integration    # actual PE simulation; requires PE country deps
uv run ruff format .
uv run ruff check .
```

CI runs unit tests on every push. The integration job is opt-in (see
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

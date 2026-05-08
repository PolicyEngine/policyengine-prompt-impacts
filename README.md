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

```bash
uv venv -p 3.13
uv pip install -e ".[dev,uk,us]"

# List registered reforms (no PolicyEngine sim required)
policyengine-prompt-impacts list

# Run all reforms and emit results
policyengine-prompt-impacts run \
  --country all \
  --json results.json \
  --tsx prompts.tsx
```

The `--tsx` output is a `UK_PROMPTS` / `US_PROMPTS` array literal ready to
paste into `TypewriterPrompt.tsx` on `policyengine-app-v2`.

## Development

```bash
uv pip install -e ".[dev]"
uv run pytest               # unit tests (no PolicyEngine sim required)
uv run pytest -m integration --runintegration  # actual PE simulation
uv run ruff format .
uv run ruff check .
```

CI runs unit tests on every push. The integration job is opt-in (see
`.github/workflows/ci.yml`) because PolicyEngine simulations take several
minutes and require HuggingFace dataset access.

## How `swap` works

Some prompts ask "who benefits from `<existing OBBBA provision>`" — the
homepage is asking about the *current law*, so the simulated reform has to
be the *repeal* of that provision and the displayed winner / loser
percentages are flipped. `Reform.swap=True` handles this:

- households that *lose* under the simulated repeal are the households
  that *benefit* from current law — these are shown as `winnerPct`
- households that *gain* under the simulated repeal are the households
  that *lose* from current law — these are shown as `loserPct`

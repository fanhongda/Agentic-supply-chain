# Eval suite

Measures whether the skill leads Claude to the right verdict on a freight invoice, and
whether it contributes anything over Claude with no skill loaded.

## Layout

```
evals/
├── corpus/<case>.yaml     # hand-authored, platform-neutral: THE SOURCE OF TRUTH
├── build.py               # adapter: corpus -> `claude plugin eval` cases
├── <case>/                # GENERATED — do not edit by hand
│   ├── prompt.md
│   └── graders/*.md
├── baseline/              # archived scores, committed
└── results/               # per-run output, gitignored
```

`corpus/` is the asset worth keeping. The generated case directories are disposable, and
a second adapter will render the same corpus into Copilot Studio Agent Evaluation test
sets — the two formats are unrelated and neither tool reads the other's files, so the
corpus is the only thing that survives the platform move.

## Running

```bash
python3 evals/build.py
```

```bash
claude plugin eval . --trust-plugin
```

Iterate on one case without the baseline arm:

```bash
claude plugin eval . --case 'c06-*' --runs 1 --ablation none --trust-plugin
```

Check the generated cases are current (for CI):

```bash
python3 evals/build.py --check
```

Each case runs 3 times with the plugin and 3 times without it. `Δ` is the difference —
what the skill contributed. A case that scores 1.00 in both arms is passing without the
skill's help.

## Cases

| Case | Class | Expected | What it pins down |
|------|-------|----------|-------------------|
| c01 express-clean | clean | ✅ | Reaches a clean verdict without inventing discrepancies |
| c02 sea-fcl-clean | clean | ✅ | BAF per TEU, 2 × 40HC counted as 4 TEU |
| c03 air-clean | clean | ✅ | Air FSC per kg of chargeable weight |
| c04 express-wrong-divisor | adversarial | ❌ | Divisor 5000 applied where the contract says 6000 |
| c05 express-stale-fuel-rate | adversarial | ❌ | Rate resolved on ship date, not invoice date |
| c06 sea-baf-as-percentage | adversarial | ❌ | BAF basis error — the headline Phase 0 fix |
| c07 air-ddp-duty-to-consignee | adversarial | ❌ | Both DDP violations caught, correct lines left alone |
| c08 sea-phantom-accessorial | adversarial | ❓ | Unquoted charges need justification, not condemnation |
| c09 express-currency-basis | adversarial | ❓ | Asks for the FX basis instead of guessing a rate |
| c10 air-weight-break-legit | **negative control** | ✅ | A cheaper higher break is not an overcharge |
| c11 air-rounding-legit | **negative control** | ✅ | A legitimate 0.5 kg round-up is not an overcharge |
| c12 non-trigger | **non-trigger** | n/a | A general shipping question gets a general answer |

The two negative controls and the non-trigger case exist to hold the false-positive rate
down. A suite of only adversarial cases rewards a skill that flags everything, and such a
skill is useless in production: every false positive costs someone an investigation and an
argument with a carrier.

## Graders

| Grader | Type | Weight | Checks |
|--------|------|--------|--------|
| `verdict` | regex | 2 | The overall verdict symbol (✅ / ❌ / ❓) under the report heading |
| `reasoning` | llm | 2 | One short rubric: is the reasoning behind the verdict right |
| `mentions-N` | regex | 1 | The load-bearing figures appear |
| `absent-N` | regex | 1 | Words that must not appear (e.g. "overcharge" on a negative control) |
| `skill-fired` | tool_used | — | The skill actually fired. Under the default ablation this is an indicator, not scored |

Two rules learned the hard way on the first pilot run, where a model response that
satisfied the rubric in full still lost 3–0:

1. **Never use PASS/FAIL for the audited invoice's own verdict inside a judge rubric.**
   The judge answers PASS/FAIL itself, and the collision flips its vote. Say "✅", or
   "the invoice can be paid as billed", instead.
2. **Keep judge rubrics short and single-focus.** The reconciliation report runs to
   thousands of characters; a five-clause conjunctive rubric over that much text makes a
   small judge model noisy. Mechanical checks belong in regex graders, which are
   deterministic, free, and read the whole message.

## Editing a case

Edit `corpus/<case>.yaml`, then re-run `python3 evals/build.py`. Never edit a generated
`prompt.md` or grader — the next build overwrites it.

Corpus fields:

| Field | Purpose |
|-------|---------|
| `id`, `title`, `mode`, `class` | Identity and grouping. `class` becomes the case's eval tag |
| `tests` | Prose: what this case pins down and why. For humans, never sent to a model |
| `expected_verdict` | `PASS` / `FAIL` / `REQUIRES CLARIFICATION` / `NOT APPLICABLE` → drives the `verdict` grader |
| `documents` | The fixture documents, inlined into the prompt. Each run starts in an empty directory, so nothing can be read from disk |
| `prompt_override` | Replaces the generated prompt outright (used by the non-trigger case) |
| `expected.must_mention` | Literal strings → one regex grader each. Keep them ≥ 4 characters, or short numbers match inside unrelated figures |
| `expected.must_not_mention` | Literal strings that must be absent |
| `expected.criteria` | The judge rubric. Short, single-focus, no PASS/FAIL vocabulary for the invoice |

All fixtures are synthetic. No real carrier invoice, rate card or counterparty belongs in
this directory — see `design.md` §8.

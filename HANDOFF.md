# Development handoff

Updated October 25, 2026 for the Jev-first implementation checkpoint.

## Current instruction

The owner selected hosted TypeSafe Jev first, classifier accuracy second, and routing/CLI development afterward. **Stop after every phase for the owner's tests and code review; proceed only when explicitly requested.** Implement only Phase 1 now. No live calls, account creation, purchases, accuracy batches, benchmarks, training, commits, or pushes are authorized by this checkpoint.

## Active implementation

- Python 3.12.15, uv/uv_build 0.11.16, no runtime dependencies beyond the standard library.
- `taxonomy.py`: three prompt-only Choice questions with explicit provisional `draft-1` definitions. Same category names as before; definitions now distinguish repair with supporting diagnosis/tests, concrete evidence, and scope actually stated in the prompt.
- `records.py`: exact UTF-8 prompt hashing/validation, labels, classification records, nullable provider token usage.
- `jev.py`: direct TypeSafe System One HTTP client pinned to `jev-1.14.0`; no retries/redirects, response validation, sanitized errors, requested/returned model IDs and latency. Constructing the client makes no call.
- `scripts/classify_prompt.py`: file/stdin input, default request preview, explicit `--live` switch using `TYPESAFE_API_KEY`. No automatic output files. Preview intentionally prints raw prompt text; live summaries omit it.
- `examples/python_bug_prompt.txt`: authored multiline review input, not a labeled accuracy dataset or result.
- Local tests in ignored `tests/` intercept HTTP and block network access. They check software behavior, not classifier quality.
- README has a GitHub Mermaid architecture diagram and exact commands for this checkpoint.

The real API code is implemented but has not been exercised against TypeSafe. No classifier accuracy, coding correctness, cost savings, or live Codex continuity is established. The script is a single-prompt review tool; the product CLI remains future work. A 16,384-byte prompt limit rejects oversized input instead of truncating. Errors return no fabricated labels; unknown categories are preserved. Missing usage and billed cost remain unavailable, including requests whose completion is uncertain.

## Preserved work and Git hygiene

The earlier fixture implementation, Codex protocol adapter, tests, original documents, and generated outputs were copied to `.local-archive/jev-first-20261025T193910Z/`. Its `manifest.json` verifies 386 original files by SHA-256, and `working-tree.patch` preserves the tracked changes from before cleanup. This is an ignored local archive, not available in a fresh clone. Do not restore it wholesale or restore the previously discarded JavaScript prototype.

The active package no longer contains simulated executors, routing/session/accounting code, or the `adaptive-code` entrypoint. Obsolete first-build defaults, test/demo instructions, and the inactive milestone schedule are archived. `/tests/`, `/.local-archive/`, and generated runs are ignored. The new local tests are intentionally absent from fresh clones. All work remains uncommitted; inspect Git status before editing and preserve existing work.

## Review commands

```sh
uv sync --offline --no-python-downloads --cache-dir .cache/uv
.venv/bin/python scripts/classify_prompt.py --prompt-file examples/python_bug_prompt.txt
.venv/bin/python -m unittest discover -s tests -v
```

Expected preview: `status: "preview"`, `request_attempted: false`, the unchanged prompt, and three questions; no predictions. Validation completed: all 24 local unit tests pass, file/stdin previews preserve input, the old entrypoint is removed, and offline wheel/source builds succeed. Package inspection confirms no tests, archive, runs, or deferred modules are shipped; local Markdown file links and `git diff --check` pass. No live API request was made. **Phase 1 is ready for owner review; stop here.** The [development plan](docs/development-plan.md) governs the next phases.

## Continuing later

Phase 2 begins only after owner instruction: TypeSafe account setup, pricing/access check, run-by-run estimate, approved cap, then one real classification before a reviewed accuracy dataset and batch. The owner currently has no provider account. OpenAI credits cannot pay TypeSafe; the reported $3,333 OpenAI balance/eligibility/expiry remain unverified. No paid work is authorized. Keep cumulative cloud/non-OpenAI cash spending strictly below $50 unless separately reviewed.

Preserve prompt-only classifier input and the separate routing policy. Compare hosted Jev, untuned/fine-tuned OpenJev, fixed/rules/cheap learned controls; hold taxonomy and policy fixed in the primary tuned/untuned comparison. Codex owns coding-session context; use one execution path for the product and benchmarks later. Category annotations and executable policy outcomes are separate evidence. SWE-bench, controlled multi-turn evaluation, and private stakeholder feedback remain planned.

The earlier live Codex account/model inspection escalation was declined. Do not retry or bypass it without renewed authorization. Keep private evidence, contacts, course submissions, raw conversations, and credentials out of Git.

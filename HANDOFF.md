# Development handoff

Updated October 28, 2026 for the stakeholder prototype Part 1 implementation.

## Current instruction

The owner authorized implementation of the five stakeholder-prototype parts, stopping after **each part** for manual tests and review: (1) single-prompt Jev routing into Codex; (2) continuity, fallback, and budgets; (3) a development-measured policy; (4) a small SWE-bench comparison; (5) repeatable demo/review material. This turn implements Part 1 only. Stop for review; do not start Part 2 or silently mark classifier accuracy complete. The latest instruction permits this integration work despite the earlier roadmap's pending accuracy checkpoint.

The owner separately authorized one standalone Jev request under the previously discussed fractions-of-a-cent estimates and reported $5 of Jev credits to use sparingly. That authorization persists but does not cover a routed coding turn. No real Jev/Codex call, account/model inspection, benchmark, training, commit, or push was performed here. Public package metadata and dependency installation were approved; they do not authorize model usage. Do not ask for credentials in chat or search unrelated credential stores.

## Active implementation

- Python 3.12.15, uv/uv_build 0.11.16. Added exact dependency `openai-codex==0.163.0`, whose bundled runtime is also pinned to `0.163.0`; `uv.lock` records dependencies. The global CLI reports `0.165.0` and is not used by the adapter. No private SDK fields are modified.
- `cli.py`: installed `adaptive-code` entrypoint with `preview`, manual-label `route`, and explicit `run --live`. Preview makes no calls or files. The terminal streams output and handles approvals explicitly; noninteractive input declines actions.
- `routing.py`: four documented Luna/Sol low/high candidates and `engineering-1`, an explicitly unvalidated mapping. Model/effort catalog eligibility is checked at runtime. Unknown categories and unavailable routes stop this slice; automatic reliable fallback and budgets remain Part 2.
- `codex_session.py`: official lower-level typed client with explicit approvals, paginated catalog discovery, requested versus accepted thread settings, one new thread/turn, streamed events, cumulative usage replacement, a process watchdog, and no automatic replay. Accepted settings are not claimed to prove provider execution settings.
- `workflow.py`: shared execution boundary for the terminal and future benchmarks. Only the exact current prompt reaches Jev; repository path and policy information stay outside its request. Codex gets the unchanged prompt and its normal tools.
- `workflow_records.py`: pending/private/atomic workflow records in ignored `runs/coding/<run-id>/workflow.json`, linked to the existing Jev attempt recorder. No raw prompt/tool output/key is persisted in these records. Missing billed cost, internal call/retry counts, execution settings, and task success stay null.
- `taxonomy.py`: three prompt-only Choice questions with explicit provisional `draft-1` definitions. Same category names as before; definitions now distinguish repair with supporting diagnosis/tests, concrete evidence, and scope actually stated in the prompt.
- `records.py`: exact UTF-8 prompt hashing/validation, labels, classification records, nullable provider token usage.
- `jev.py`: direct TypeSafe System One HTTP client pinned to `jev-1.14.0`; no retries/redirects, response validation, sanitized errors, requested/returned model IDs and latency. Constructing the client makes no call.
- `run_records.py`: writes a private pending record before dispatch, then atomically saves the validated result or sanitized error in ignored `runs/jev/<run-id>/attempt.json`. Records hashes, fixed questions/snapshot, IDs, UTC timestamps, model, usage, and a dated cost estimate. No raw prompt or key is saved. Pending/interrupted attempts are uncertain and never replayed automatically; final storage failure exposes the observed result for recovery.
- `scripts/classify_prompt.py`: file/stdin input, default request preview, explicit `--live` switch using `TYPESAFE_API_KEY`, optional `--example-id` and `--run-dir`. Preview prints the request and writes no files; live attempts use the recorder. Missing credentials produce a local error record with no HTTP request.
- `jev.py` now preserves a valid returned model on answer-validation errors so reported usage can still receive a clearly labeled estimate. The client otherwise keeps the same request and category behavior.
- `examples/python_bug_prompt.txt`: authored multiline review input, not a labeled accuracy dataset or result.
- Local tests in ignored `tests/` intercept HTTP and block network access. They check software behavior, not classifier quality.
- README has a GitHub Mermaid architecture diagram and exact commands for this checkpoint.

The real API code is implemented but has not been exercised against TypeSafe or live Codex here. No classifier accuracy, coding correctness, cost savings, or live continuity is established. The new terminal is a single-prompt integration slice; Part 2 adds continuation/resume. A 16,384-byte prompt limit rejects oversized input without truncation; product fallback for oversized/unknown input remains future work. The provisional mapping is not backed by development outcomes. Jev estimates still use the dated October 27 rate only for the pinned returned model; missing usage or another model leaves the estimate unavailable. The watchdog closes the Codex process, while Jev has its own socket timeout. Neither is dollar-budget enforcement.

## Preserved work and Git hygiene

The earlier fixture implementation, Codex protocol adapter, tests, original documents, and generated outputs were copied to `.local-archive/jev-first-20261025T193910Z/`. Its `manifest.json` verifies 386 original files by SHA-256, and `working-tree.patch` preserves the tracked changes from before cleanup. This is an ignored local archive, not available in a fresh clone. Do not restore it wholesale or restore the previously discarded JavaScript prototype.

The previous simulation implementation was not restored. New routing/session code and the `adaptive-code` entrypoint were implemented for this slice around the official SDK. Obsolete first-build defaults, test/demo instructions, and the inactive milestone schedule stay archived. `/tests/`, `/.local-archive/`, and generated runs are ignored; local tests are intentionally absent from fresh clones. Existing edits to AGENTS, the Jev client/recorder/script, packaging, and documentation were preserved. This checkpoint is uncommitted with new source/packaging files still untracked. Inspect Git status before editing; do not attribute all preexisting changes to this turn.

## Review commands

```sh
uv sync --locked --offline --no-python-downloads --cache-dir .cache/uv
.venv/bin/adaptive-code preview --prompt-file examples/python_bug_prompt.txt
.venv/bin/adaptive-code route --task-type fix --cause-evidence supporting_details --change-scope localized
env -u TYPESAFE_API_KEY .venv/bin/adaptive-code run --prompt-file examples/python_bug_prompt.txt --live
.venv/bin/python scripts/classify_prompt.py --prompt-file examples/python_bug_prompt.txt
env -u TYPESAFE_API_KEY .venv/bin/python scripts/classify_prompt.py --prompt-file examples/python_bug_prompt.txt --example-id no-key-check --live
.venv/bin/python -m unittest discover -s tests -v
```

Expected preview: `status: "preview"`, `request_attempted: false`, the unchanged prompt and three questions; no predicted categories or files. Manual-label routing selects Luna/low and identifies its policy as unvalidated. The `env -u` commands exit 1 with `missing_credentials` and a saved record, with no HTTP or Codex startup; the parent's key is unchanged. The original 40 tests plus 21 new checks cover the actual SDK against an offline JSON-RPC test server, including notification/response races, catalog pagination, exact prompt boundaries, setting mismatches, approval denial, usage deduplication, timeouts/disconnection, rerouting, and storage failure. Mocked responses are not research results. See README for the Part 1 commands and limits.

Run once in the owner's terminal, where the key is exported:

```sh
.venv/bin/python scripts/classify_prompt.py --prompt-file examples/python_bug_prompt.txt --example-id first-live-check --live
```

Before any retry, inspect the saved `record_path`. No potential live-attempt record was found under `runs/jev/` at the October 28 check. A pending/interrupted attempt remains uncertain and must not be replayed automatically.

## Continuing later

Next: owner manual review of Part 1. A scoped live-integration estimate, permitted authentication/billing path, and renewed authorization for the previously declined account/model inspection are still needed before the agent runs the new coding path. Do not claim the Part 1 live acceptance check has passed. The earlier standalone Jev authorization remains separate: its one-call scenarios were $0.000084 at 2,000 input tokens or $0.00084 at 20,000, illustrative rather than measured bills. The assistant's former $0.01 planning ceiling was not a user-selected cap. The reported $5 balance is not permission for a batch. Classification accuracy, labeled data, later prototype parts, fine-tuning, and paper experiments remain pending. Keep cumulative cloud/non-OpenAI cash spending strictly below $50 unless separately reviewed.

Preserve prompt-only classifier input and the separate routing policy. Compare hosted Jev, untuned/fine-tuned OpenJev, fixed/rules/cheap learned controls; hold taxonomy and policy fixed in the primary tuned/untuned comparison. Codex owns coding-session context; use one execution path for the product and benchmarks later. Category annotations and executable policy outcomes are separate evidence. SWE-bench, controlled multi-turn evaluation, and private stakeholder feedback remain planned.

The earlier live Codex account/model inspection escalation was declined. Do not retry or bypass it without renewed authorization. Keep private evidence, contacts, course submissions, raw conversations, and credentials out of Git.

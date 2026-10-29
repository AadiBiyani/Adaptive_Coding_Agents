# Development handoff

Updated October 29, 2026. README remains the overall project summary with its full architecture diagram. Keep temporary review instructions here.

## Current owner instruction and pause point

The owner requested a ChatGPT-style JavaScript/React/shadcn frontend, then a Tests tab and a clean frontend/backend layout. This slice is implemented and verified offline. Stop for the owner's manual review before additional product or research phases. Part 3's development-measured policy, SWE-bench execution, and OpenJev training have not started.

**Only the owner performs actions that consume model tokens or money.** Agents may write code and run offline checks. Do not send coding prompts, run a live classifier batch, or start training on the owner's behalf. No paid inference was executed during this UI/testing/cleanup slice.

## Layout and entry points

- `frontend/`: JavaScript/JSX React app, Vite, Tailwind, and actual generated shadcn/ui components.
- `backend/src/adaptive_coding_agents/`: Python API, Jev client, routing, shared Codex workflow, budgets, sessions, and local evaluation jobs.
- `backend/scripts/`: classifier pilot preparation and the original classifier script still exercised by regression tests. The original script bypasses the newer budget; use the budgeted CLI for live requests.
- Root `pyproject.toml` and `uv.lock`: Python dependency/packaging entry point, with `module-root = "backend/src"`. Existing `.venv/bin/adaptive-code` commands, `.env`, and data paths remain valid.
- Ignored `tests/`: local regression and rendering checks. These are deliberately absent from fresh clones.
- Ignored `runs/`: coding records, budgets, native-session handles, browser transcripts, evaluation reports, and default workspace.
- `docs/`: retained project, architecture, evaluation, training, and research plans.

The source move verified every moved file's hash before and after. Removed the unused frontend class-name helper and its direct dependencies, the unused preview command, stale generated schema/build outputs, and Python bytecode caches. Kept the installed environments, useful dependency caches, research documents, private records, and the owner's ignored historical archive. Nothing was committed or pushed.

## Implemented product

The Python backend uses the official `openai-codex==0.163.0` SDK and matching runtime. The terminal and browser call the same `run_prompt`; there is no second coding harness. Hosted TypeSafe requests pin `jev-1.14.0`, use the three fixed Choice questions, preserve missing usage, reject inputs over 16,384 UTF-8 bytes unchanged, and do not retry automatically.

Jev receives only the exact newly submitted prompt plus fixed taxonomy definitions. Codex retains conversation/repository/tool context. The classifier returns labels; a separate provisional `engineering-2` policy selects Luna/Sol at low/high effort. Unknown labels can use eligible Sol/high fallback. This mapping has no measured reliability advantage. Invalid/provider-failed classifications stop.

The adapter preserves explicit approvals, checks API-key authentication and ephemeral credential storage, verifies catalog and accepted settings, resumes sessions, and records requested/accepted/observed configurations separately. Cancellation closes the owned process without replay. Uncertain billing retains reservations and blocks continuation.

The React interface includes arbitrary coding prompts, incremental Markdown responses, copyable code, conversation history, routing details, approvals, stop, workspace selection/file previews, and light/dark modes. Files are written to the selected workspace; the default is `runs/workspaces/default/`. Browser prompt/response text and visible tool output are privately saved in `runs/ui/chats/`. Old CLI metadata cannot reconstruct response text.

Spending reprices observed input/cache/output buckets for a selected fixed configuration, defaulting to Sol/high from the registry. It never runs that baseline. The routed side includes Jev's estimate. Dated rates and assumed cache lifetime are explicit, reasoning is not counted twice, and effort has no invented multiplier. These are pricing scenarios, not invoices, measured savings, or predictions of another model's token use. Resumed thread snapshots are labeled and never summed across runs.

## Tests & analysis

`evaluations.py` manages named local adapters; `evaluation_worker.py` produces structured unittest results in a separate process. The React Tests tab supports:

- **Project checks:** the local Python suite for classifier contracts, routing, accounting, sessions, UI, and evaluation jobs.
- **Frontend checks:** real React rendering checks without a browser or model call.
- **Workspace tests:** trusted Python `unittest` files matching `test*.py` in the selected coding folder or a relative test subdirectory.

Only a user-triggered Run starts a job. Duplicate IDs cannot replay it, one job runs at a time, and the browser prevents overlapping coding/test work through backend checks. Reports include progress, individual outcomes, bounded output, source fingerprints before/after, command/environment metadata, elapsed time, cancellation/timeouts, history, and JSON export. Empty suites and all-skipped suites are not reported as passes. Reports persist privately in `runs/evaluations/<id>/run.json`; restart marks unfinished jobs interrupted without replay.

The runner strips inherited credentials. Workspace mode blocks ordinary Python network and child-process calls, but is **not an untrusted-code sandbox**. Do not run downloaded benchmark repositories on the host. Pytest-only suites or separate project environments are not supported by this slice. No model request is initiated by these adapters, and local results are not SWE-bench scores or independent claims that an agent solved a task.

The UI is a foundation for later SWE-bench task/strategy analysis, not an implementation of the isolated evaluator. The separately budgeted classifier pilot remains a terminal operation after human annotation.

## Verification and measured evidence

All **118 offline Python tests passed** after the reorganization. The updated HTTP integration check also passed, exercising authenticated test submission, progress/results, duplicate protection, and an unchanged budget with an authored workspace fixture. React rendering and the production frontend build pass. Source distribution and wheel build under `.cache/build/`; inspection includes the UI/evaluation modules and excludes secrets, tests, run data, and node_modules.

Both project and frontend adapters were then run through the actual localhost API. Project checks passed all 118 tests; the frontend rendering check passed. Their saved reports are:

- `runs/evaluations/02865125-01ed-4fc2-afdc-d6f59454346d/run.json`
- `runs/evaluations/2fde63a9-325e-4755-9c0b-cee78b804b57/run.json`

The budget file was byte-for-byte unchanged across those API checks. These are real software-check results using mocked providers where appropriate, not research outcomes. Browser automation was unavailable; do not claim screenshot or visual interaction verification.

The owner has run two paid coding turns. The first workflow, `runs/coding/f03dc87e-9892-402d-aaa2-d773f9853320/workflow.json`, selected/accepted Luna/low and repaired an authored empty-list bug. An independent rerun passed all three unchanged tests. Its session is `40bc5b35-64d9-4539-beb3-0cdad20b463a`, workspace `/private/tmp/adaptive-coding-agents-part2-plzv124v`.

The second owner-run workflow, `runs/coding/3eea61b1-5eff-45e7-9be3-de1b9e81d509/workflow.json`, is recorded completed in the default browser workspace with estimated accounting and continuation allowed. Completion alone is not an independent task-success result. Neither run is SWE-bench evidence. Live session resumption/configuration-change/fallback verification remains pending.

## Spending and remaining work

The reviewed shared allocation is $0.05 Jev and $2 OpenAI, with 43 Jev requests and three coding turns. At the latest check two Jev requests and two coding turns were used; **one coding turn remains**. The recorded remaining admission amounts are $0.049922258 Jev and $1.97738875 OpenAI. They are not actual account balances or bills. Do not reset/increase the ledger or treat available credits as authorization. Cumulative cloud/non-OpenAI cash spending must remain below $50 unless separately reviewed.

The classifier pilot has 20 development and 20 held-out authored prompts under ignored `data/classifier-pilot.json`. Labels remain unreviewed; no accuracy batch has run. `GROUPS` is split/group metadata, not a lookup from problems to executable tests. Human annotations must use only the current prompt. Held-out evaluation requires the frozen development report; no predictions may become their own gold labels.

The primary future study remains fine-tuned versus untuned OpenJev with matched base checkpoint, taxonomy, downstream policy, harness, and evaluation conditions. Hosted Jev is a distinct comparison. Keep fixed, rule-based, and cheap learned controls; independent executable SWE-bench checks; controlled multi-turn analysis; grouped splits; cost/uncertainty reporting; and stakeholder review. No training, routing-quality, savings, novelty, or course-completion result has been established.

## Manual review

From the repository root:

```sh
uv sync --locked
npm ci --prefix frontend
npm run build --prefix frontend
.venv/bin/adaptive-code ui
```

Open `http://127.0.0.1:8765`. The app was restarted after the folder move. Opening it and using Tests or Spending requires no inference. In Tests, run Project checks, then Frontend checks. To inspect generated-code tests, choose Workspace tests; use `.` for a root `test_cart.py` or `tests` for a subfolder. Inspect failures, history, and exported details.

For coding review, only the owner sends a prompt. Select a workspace, inspect its route/response/files, and use the remaining coding turn deliberately; UI and CLI share the same cap. A new conversation starts a new Codex session; a follow-up in the existing conversation resumes it.

Free local verification, when the ignored tests are present:

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/ui-render.mjs
.venv/bin/adaptive-code credentials
.venv/bin/adaptive-code budget status
```

The HTTP tests need permission to bind loopback ports. `tests/smoke_ui_evaluations.py` checks both offline adapters through the running UI and verifies an unchanged API budget. It does not submit chat prompts or classifier requests.

The owner committed Part 1 as `fdd6830`; subsequent work remains uncommitted. Keep stakeholder evidence, personal contacts, course submissions, raw conversations, secrets, datasets, and generated reports out of Git. The ignored archive `.local-archive/jev-first-20261025T193910Z/` stays preserved. Stop here for review.

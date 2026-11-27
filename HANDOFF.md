# Development handoff

Updated November 27, 2026. README remains the overall project summary with its full architecture diagram. Keep temporary review instructions here.

## November 27 Windows-to-Mac handoff

The final CUDA reserve is complete. The reproducible, repository-balanced selection froze 48 SWE-bench Verified issue groups across ten repositories and six controlled scenarios across six repositories. Both CUDA classifiers covered all 48 initial messages and all 12 possible follow-ups, totaling 360 field decisions. Blind verification passed for both batches. The outcome-free receipts and timing records are under `runs/openjev/final-reserve-cache-v1/verification/`. Restrict the final prediction files, comparisons and sealed logs until the development-based sampling and evaluation decisions are recorded. All six public checks passed Python syntax compilation; their behavior still needs isolated validation.

Download both private archives from OneDrive Desktop/Adaptive_Coding_Agents/runs/openjev. A clean-directory Windows restore of both archives verified the payloads, both caches and the frozen adapter's 32 tensors and 1,114,112 parameters. Windows reported both ZIPs and both checksum sidecars in sync. The outcome-free source-side receipt is `runs/openjev/study-1-final-reserve-v1-windows-verification.json`. Mac download, destination verification and E007b native MLX validation remain pending.

| Archive | Bytes | SHA-256 |
|---|---:|---|
| `study-1-handoff.zip` | 111,697,797 | `aac19a92a0525c5d356de50d543964da29ca73c312c266e9abd7ea005f44fc2e` |
| `study-1-final-reserve-v1-supplement.zip` | 4,361,504 | `cac9af90912fd17116ff210c1de6e22cf6cae40430929d26afcc9d02db2c4740` |

The [final reserve handoff](docs/final-reserve-handoff.md) contains the restore commands, Windows selection replay and Mac roadmap. Integrate cache lookup and the isolated grader on the six development issues first. Use development costs and variability to approve a budget, reliability margin, precision target and prefix of 12, 24, 36 or 48 before opening independent outputs. Continue with matched downstream coding, claim-specific ablations, paired statistical analysis and the research paper. Exact frozen messages can use the CUDA caches on the Mac without running either model. Live new prompts need validated local inference or a new authoritative cache.

The owner completed both CUDA cache exports. E007a compared each variant's 20 reloaded development rows with its original report. All 200 candidate logits per variant matched exactly, with 60/60 matching labels and 20/20 matching routes per variant. The reference set also includes the synthetic fixture. The private handoff uses `runs/openjev/study-1-handoff.zip` and a separate `.zip.sha256` receipt. The archive's `handoff/` directory contains the machine-readable replay report, member checksums, Mac dependency lock and wheels, and restore instructions. Use the contract-matching working source at the archive root when restoring the study, including `training/openjev/dataset.py`.

The first archive includes the six development issues and the 21-message portability reference. The supplemental archive supplies the disjoint final reserve. Use only the development and reference panels for Mac implementation work.

## November 26 benchmark prompt freeze

The owner completed the independent 20-prompt held-out comparison with frozen epoch 2. Exact three-label agreement was 17/20 for untuned Flash and 18/20 for tuned Flash. Two routes changed. Both variants agreed with the policy applied to the reviewed labels on 19/20 prompts. The private reports are in `runs/openjev/study-1/held-out/`.

The owner chose a six-issue development pilot across three Python repositories. The private `data/frozen-benchmark-prompts.json` contains six original SWE-bench Verified issue messages and six authored follow-ups. `data/frozen-benchmark-scenarios.json` pins the upstream revision, base commits, selection order and exclusions, message hashes, and visible branch checks for three controlled scenarios. Reserve the six groups and their derivatives from the final downstream test cohort. All 36 formatted questions fit the frozen 512-token limit. The cache fingerprint is `7687cbf0797bb43fe82abb61f15ce94889095e7291493147003c27bd9077190b`.

The matched cache export is complete. Public branch checks still need to be exercised in the isolated task environments. Grader and image digests, budgets, and downstream execution remain open.

## Local OpenJev work resumed November 25

The owner resumed local Flash 9B classifier work on a Windows RTX 3060 with 12 GiB VRAM. The owner authorized public downloads and a synthetic GPU feasibility check and will operate the research fine-tuning run personally. A formal stakeholder prototype or rubric review remains unverified. Ask before any paid provider or cloud run.

The model, tokenizer and choice helper are pinned to `openjev/OpenJev-Flash-9B` revision `b77b0fff67c77a76c16d4da50a66d2fdbc124fae`. The owner reviewed all 84 active training prompts across 42 issues. The original 12 across six issues have 28 verbatim evidence quotes in `data/review/training-evidence-review.csv`. The owner reviewed the next 72 prompts across six private sheets, `data/review/batches/training-01.csv` through `training-06.csv`, and revised four field labels. All 207 final evidence quotes match the exact prompts. The two previously excluded rows remain excluded. The private `data/review/review-manifest.json` records canonical dataset and review-sheet checksums plus the experiment split hashes.

The owner independently labeled all 20 development and all 20 held-out prompts before seeing predictions. All 40 saved annotations match the owner's review sheets. IDs, issue groups, exact prompts and split assignments match the original pilot preparation script. Each five-row sheet used opaque IDs and five distinct issues. Keep held-out outcomes sealed until the checkpoint is selected on development and frozen.

The pinned tokenizer formatted all 372 prompt–question pairs within the 512-token limit. Maximum lengths were 215 tokens for training, 220 for development and 217 for held-out.

The owner completed the untuned Flash 9B development baseline in `runs/openjev/study-1/base-development.json`. All 20 rows match the reviewed development inputs and all 60 option-score vectors are finite. Correct field counts were 18/20 for task type, 20/20 for cause evidence and 19/20 for change scope. Mean field macro-F1 was 0.9466 and exact three-label agreement was 17/20. The policy produced the same route from predicted and reviewed labels on 19/20 prompts. Scoring took 18.29 seconds across the 20 rows, excluding model loading. The contract's split hashes match the review manifest.

The owner trained a QLoRA adapter on the RTX 3060 for two epochs of 252 field decisions each. Both epochs matched all three labels on 20/20 development prompts and achieved mean field macro-F1 of 1.0000. The development loss tiebreak selected epoch 2 (0.00446 versus 0.02677 for epoch 1). The epoch 2 adapter and configuration checksums match `runs/openjev/study-1/freeze.json`. Relative to the untuned baseline, the frozen adapter corrected two task types and one scope. One correction changed the selected model from Luna to Sol at high effort. The other 19 routes stayed the same. SWE-bench outcomes and cost per resolved issue remain unmeasured.

The owner completed synthetic run `smoke-20261125-113447` with PyTorch 2.13.0+cu130. The saved reports record 32 changed adapter tensors, 7,870 MiB peak reserved GPU memory, 12 timed field decisions in 15.85 seconds, and zero maximum logit difference on a fresh-process reload. Both synthetic predictions selected `luna-low`.

Use the [GPU-to-Mac checklist](docs/gpu-to-mac.md) for the OneDrive restore rehearsal, package snapshot, owner-operated training stages, matched prompt exports, and final archive verification. The independent file reader passed on the original PC adapter. OneDrive retrieval and native MLX inference still need verification on the Mac. The [RTX 3060 plan](OpenJev_3060_Training_Plan.md) records the experiment design.

The pre-training Windows snapshot is in ignored `runs/openjev/environment-study-1/`. It captures Python 3.12.16, the installed packages and CUDA wheel, runtime and driver details, the Git revision, and the working source including the uncommitted Mac checker and documentation. Its manifest records checksums. The owner confirmed visibility in OneDrive from the Mac and plans to test the Mac implementation after training. The research baseline will record its own source revision.

## November 9 demo checkpoint (historical)

The owner reviewed and committed the React frontend and frontend/backend layout as `8f33152`. Subsequent slices added the 40-prompt classifier pilot, removed software checks from the frontend, and added per-turn Jev probabilities and routing explanations. The latest request is to implement separate per-chat, shared-dollar, and experiment controls, then **stop development for Ryan's demo and feedback**. Those controls are now implemented and verified offline, with a 10-user-turn demo default. The existing local ledger has been migrated with all charges and dollar caps preserved. Manual UI review and live messages remain owner actions. Do not proceed to Parts 3–5 until the owner resumes after feedback; this supersedes the earlier authorization to continue. OpenJev training has not started.

**Only the owner performs actions that consume model tokens or money.** Agents may write code and run offline checks. Do not send coding prompts, run a live classifier batch, or start training on the owner's behalf. No paid inference was executed during this UI/testing/cleanup slice.

## Layout and entry points

- `frontend/`: JavaScript/JSX React app, Vite, Tailwind, and actual generated shadcn/ui components.
- `backend/src/adaptive_coding_agents/`: Python API, Jev client, routing, shared Codex workflow, budgets, sessions, and local evaluation jobs.
- `backend/scripts/`: classifier pilot preparation and the original classifier script still exercised by regression tests. The original script bypasses the newer budget; use the budgeted CLI for live requests.
- Root `pyproject.toml` and `uv.lock`: Python dependency/packaging entry point, with `module-root = "backend/src"`. Existing `.venv/bin/adaptive-code` commands, `.env`, and data paths remain valid.
- Ignored `tests/`: local regression and rendering checks. These are deliberately absent from fresh clones.
- Ignored `runs/`: coding records, budgets, native-session handles, browser transcripts, evaluation reports, and default workspace.
- `docs/`: retained project, architecture, evaluation, training, and research plans.

The source move verified every moved file's hash before and after. Removed the unused frontend class-name helper and its direct dependencies, the unused preview command, stale generated schema/build outputs, and Python bytecode caches. Kept the installed environments, useful dependency caches, research documents, private records, and the owner's ignored historical archive. The owner subsequently committed that work; the classifier-pilot, classification-panel, and demo-control changes are now in separate backend and frontend commits.

## Implemented product

The Python backend uses the official `openai-codex==0.163.0` SDK and matching runtime. The terminal and browser call the same `run_prompt`; there is no second coding harness. Hosted TypeSafe requests pin `jev-1.14.0`, use the three fixed Choice questions, preserve missing usage, reject inputs over 16,384 UTF-8 bytes unchanged, and do not retry automatically.

Jev receives only the exact newly submitted prompt plus fixed taxonomy definitions. Codex retains conversation/repository/tool context. The classifier returns labels; a separate provisional `engineering-2` policy selects Luna/Sol at low/high effort. Unknown labels can use eligible Sol/high fallback. This mapping has no measured reliability advantage. Invalid/provider-failed classifications stop.

The adapter preserves explicit approvals, checks API-key authentication and ephemeral credential storage, verifies catalog and accepted settings, resumes sessions, and records requested/accepted/observed configurations separately. Cancellation closes the owned process without replay. Uncertain billing retains reservations and blocks continuation.

The React interface includes arbitrary coding prompts, incremental Markdown responses, copyable code, conversation history, approvals, stop, workspace selection/file previews, and light/dark modes. Every turn now shows a dedicated Jev panel with reported option probabilities for all three category fields, selected labels, the policy reason, selected model/effort, accepted settings when available, and a configuration change from the previous turn. Provider confidence is separate from option probabilities; neither is a coding-success/model-selection probability. The policy currently uses selected labels, not confidence thresholds. The mapping remains unvalidated.

The shared workflow emits `classification/completed` and persists a prompt-free `prompt-classification-view-1` summary in each workflow record; the UI also saves it in the corresponding chat turn. Existing browser turns recover missing summaries from matching, path-scoped local records without calls or rewriting history. Missing scores remain unavailable. These shared records are ready for later multi-turn benchmark analysis; no benchmark controller has been implemented. Files are written to the selected workspace; the default is `runs/workspaces/default/`. Browser prompt/response text and visible tool output are privately saved in `runs/ui/chats/`. Old CLI metadata cannot reconstruct response text.

Spending reprices observed input/cache/output buckets for a selected fixed configuration, defaulting to Sol/high from the registry. It never runs that baseline. The routed side includes Jev's estimate. Dated rates and assumed cache lifetime are explicit, reasoning is not counted twice, and effort has no invented multiplier. These are pricing scenarios, not invoices, measured savings, or predictions of another model's token use. Resumed thread snapshots are labeled and never summed across runs.

The Spending control table separates **10 user turns per chat**, **shared cumulative provider dollar caps**, and **experiment request quotas**. A new chat/session gets a fresh turn allowance; reopening or resuming keeps the count. Accepted failed/cancelled runs count, while duplicate submission IDs cannot replay or consume another turn. Internal model/tool calls are not extra user turns. The backend enforces the limits in both browser and terminal. Money and experiment usage never reset on a new chat. Named experiment allocations are supported by `budget experiment` and `run --experiment`; this is accounting support, not a benchmark runner, and no additional experiment has been allocated.

## Evaluation and software checks

Software-check selection, Run/Stop controls, test history, and local-test results have been removed from the frontend at the owner's request. Use the terminal commands below for Python regression checks and React rendering checks. Existing backend local evaluation adapters, private reports, and developer API tests remain available; they are no longer a product UI. Their trusted-workspace runner is not an untrusted-code sandbox. Do not run downloaded benchmark repositories on the host.

The renamed **Evaluation** page explains the classifier pilot and provides its review/results flow. It is a foundation for later SWE-bench task/strategy analysis, not an implementation of the isolated evaluator.

**40-prompt Jev pilot.** The Evaluation page exposes the 20-development/20-held-out authored diagnostic dataset. `classifier_pilot.py` manages review and confirmed browser jobs. `classifier_evaluation.py` remains the shared CLI/browser evaluator. The frontend shows one prompt with the fixed category definitions and accepts owner-reviewed labels. The November 25 offline review supplied all 40 labels. The prompts serve as classifier evaluation inputs.

The owner previews one split's costs, then explicitly confirms. The confirmation shows Jev requests and zero OpenAI calls: this cohort evaluates classification, not executable coding tasks. The current conservative admission estimate is $0.02 for 20 prompts ($0.04 across both splits), not a guaranteed bill. The existing shared caps and attempt limits are rechecked without increasing/resetting them. Short-lived confirmations bind the exact split, reviewed labels, questions, requested classifier, and development freeze; changed inputs require a new preview. Duplicate submissions cannot repeat a batch. Cancellation lets an in-flight request finish accounting and stops before the next prompt. Coding and local checks cannot overlap a classifier batch.

Held-out execution requires a matching completed development report; annotations become read-only once predictions exist for their split. Live progress, accuracy/macro-F1, exact match, individual label comparisons, failure counts, cost estimates, history, and exports appear in the UI. Reports retain full confusion matrices, usage, latency, hashes, and budget records under ignored `runs/classifier-evaluation/`. No classifier batch was executed during implementation. These labels/results cannot establish a measured model/effort routing policy; Part 3 needs separate executable configuration outcomes.

## Verification and measured evidence

Earlier verification passed all **142 offline Python checks**, including prompt-only classification, per-turn records, historical evidence recovery, pilot confirmation/cancellation, and the localhost API. New checks cover migration with unchanged charges/caps, per-chat reset and persistence, duplicate submissions, shared-dollar exhaustion, independent experiment quotas, and CLI session enforcement. That suite ran with loopback permission and mocked inference only. React rendering checks verify the probability panel, unavailable/error states, routing changes, pilot confirmation, the new control table, and the absence of software checks. The production frontend build passes with the existing bundle-size warning. No visual browser automation was available.

Pre-commit verification on November 9 passed 141 of 142 Python checks; the HTTP check could not bind localhost because of the session's sandbox restriction (`PermissionError`). React rendering and the production frontend build passed again. No model calls were made. Rerun the full Python command below from the owner's terminal to verify the localhost check.

Before this slice, source distribution and wheel builds passed under `.cache/build/`; their inspection included UI/evaluation modules and excluded secrets, tests, run data, and node_modules. The following earlier localhost adapter runs remain historical verification of the previous 118-check suite:

Both project and frontend adapters were then run through the actual localhost API. Project checks passed all 118 tests; the frontend rendering check passed. Their saved reports are:

- `runs/evaluations/02865125-01ed-4fc2-afdc-d6f59454346d/run.json`
- `runs/evaluations/2fde63a9-325e-4755-9c0b-cee78b804b57/run.json`

The budget file was byte-for-byte unchanged across those API checks. These are real software-check results using mocked providers where appropriate, not research outcomes. Browser automation was unavailable; do not claim screenshot or visual interaction verification.

The owner has run two paid coding turns. The first workflow, `runs/coding/f03dc87e-9892-402d-aaa2-d773f9853320/workflow.json`, selected/accepted Luna/low and repaired an authored empty-list bug. An independent rerun passed all three unchanged tests. Its session is `40bc5b35-64d9-4539-beb3-0cdad20b463a`, workspace `/private/tmp/adaptive-coding-agents-part2-plzv124v`.

The second owner-run workflow, `runs/coding/3eea61b1-5eff-45e7-9be3-de1b9e81d509/workflow.json`, is recorded completed in the default browser workspace with estimated accounting and continuation allowed. Completion alone is not an independent task-success result. Neither run is SWE-bench evidence. Live session resumption/configuration-change/fallback verification remains pending.

## Spending and remaining work

The reviewed shared allocation remains **$0.05 Jev and $2 OpenAI**. On October 30 the owner's requested adjustment migrated `runs/part-2-budget.json` to `admission-budget-2`: each chat/session has 10 user turns, and `classifier-pilot` has 40 Jev requests plus zero coding turns across both splits. The former global 43-request/three-turn ceilings are replaced; neither dollar cap increased. All four existing entries (two Jev and two coding attempts), their charges, and remaining amounts were verified unchanged. The private backup is `runs/part-2-budget.json.before-chat-controls.json`.

The recorded remaining admission amounts are **$0.049922258 Jev and $1.97738875 OpenAI**; the classifier experiment has used zero of its 40 requests. These are ledger estimates, not actual account balances or bills. Shared caps, reservations, and uncertainty can stop work before a chat uses all ten turns. Opening a new chat never refills money or experiment requests. The migration made no provider calls. Do not reset/increase the ledger or treat available credits as authorization. Cumulative cloud/non-OpenAI cash spending must remain below $50 unless separately reviewed.

The classifier pilot has 20 development and 20 held-out authored prompts under ignored `data/classifier-pilot.json`. The owner has reviewed all 40. The hosted Jev pilot still awaits scoring. `GROUPS` records the pilot's split and issue assignments. Human annotations use only the current prompt. Held-out evaluation requires the development freeze.

The primary future study remains fine-tuned versus untuned OpenJev with matched base checkpoint, taxonomy, downstream policy, harness, and evaluation conditions. Hosted Jev is a distinct comparison. Keep fixed, rule-based, and cheap learned controls; independent executable SWE-bench checks; controlled multi-turn analysis; grouped splits; cost/uncertainty reporting; and stakeholder review. No training, routing-quality, savings, novelty, or course-completion result has been established.

## Manual review

From the repository root:

```sh
uv sync --locked
npm ci --prefix frontend
npm run build --prefix frontend
.venv/bin/adaptive-code ui
```

Restart the backend in the owner's terminal after rebuilding, then open `http://127.0.0.1:8765`. The agent previously stopped its background server at the owner's request; do not assume any current listener belongs to the agent. Opening the app, viewing Spending, reviewing saved classifications, and annotating labels require no inference. Software checks now run from the terminal. Inspect an existing saved chat to see its Jev probabilities and policy explanation without spending.

For the classifier pilot, open **Evaluation** and read its explanation. Review and save the three labels for each development prompt from its text alone. After all 20 are reviewed, choose **Review cost & run Jev tests**. Inspect both provider counts and Cancel to test the no-spending path. Only the owner should choose **Confirm & spend Jev tokens**. Inspect the completed development report; review the held-out labels independently and choose that development report as the freeze before confirming the second batch. Do not use predictions as gold labels or change the classifier after seeing held-out outcomes. Shared-budget exhaustion remains a stop, not permission for an increase.

For the free controls check, open Spending and inspect its three-row table and unchanged shared dollar caps. Open New chat and verify 10 turns remain; reopen an existing chat and verify its existing turns count. Neither action changes the dollar or experiment totals. Only the owner sends live prompts. A submitted message consumes one chat turn; follow-ups resume the existing Codex session. The offline suite already checks cap exhaustion, so there is no need to pay for ten prompts just to verify the limit.

Free local verification, when the ignored tests are present:

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/ui-render.mjs
.venv/bin/adaptive-code credentials
.venv/bin/adaptive-code budget status
```

The HTTP tests need permission to bind loopback ports. `tests/smoke_ui_evaluations.py` checks both offline adapters through the running UI and verifies an unchanged API budget. It does not submit chat prompts or classifier requests.

The owner committed Part 1 as `fdd6830` and the chat/test UI plus reorganization as `8f33152`. At the owner's request, the subsequent backend changes are committed as `33a6e0e` and the frontend changes as `2bc4eac`, with documentation in a separate commit. Pushing to main remains the owner's action. Keep stakeholder evidence, personal contacts, course submissions, raw conversations, secrets, datasets, and generated reports out of Git. The ignored archive `.local-archive/jev-first-20261025T193910Z/` stays preserved. **Development stops here for Ryan's review and feedback.** Resume only when the owner requests it. No paid calls or new research results were produced during this slice.

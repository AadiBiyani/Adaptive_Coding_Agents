# Conservative defaults for the first build

Selected October 24, 2026 after the owner delegated the remaining engineering defaults and said development would start tomorrow. Tonight is documentation only. This closes the contract for the first offline foundation; live integration, benchmark/data design, and training retain their later validation gates. No application code, environment installation, model call, or cloud job was created.

## First implementation boundary

Build a small Python package containing records/validation, prompt encoding, configuration eligibility, deterministic policy lookup and fallback, usage/event accounting, and simulated classifier/executor adapters. Use explicit fixtures to exercise the complete local path. Default mode is `offline`; live providers and the Codex subprocess are not enabled in this slice. Simulated choices, usage, and outputs are labeled as fixtures and cannot be reported as model or benchmark results.

The planned terminal entry point is `adaptive-code`, with `python -m adaptive_coding_agents` available during development. Do not create another coding harness. The later real executor will wrap the selected Codex app-server interface behind the same application boundary.

## Runtime and dependency defaults

| Item | Selected default |
| --- | --- |
| Application Python | Python 3.12 in a project `.venv` managed by uv; resolve and record the exact installed patch during setup. Do not change the system Python. |
| Current local observations | `python3 --version`: 3.9.6; `uv --version`: 0.11.16; `codex --version`: 0.164.0. Read-only checks were repeated October 24. No app-server/account inspection was attempted. |
| Offline runtime dependencies | Standard library initially: typed records, enums, JSON, hashing, decimal money, and local event files. No SDK/HTTP/model dependency is needed for fixtures. |
| Offline verification | Standard-library unittest initially, focused on input isolation, eligibility, fallback, accounting, and state transitions. Dependency additions need a concrete purpose and exact lock when introduced. |
| Real Codex client | Keep the reviewed 0.164.0 protocol as the initial target. Verify the published Python SDK distribution, its runtime pin, and explicit approval-handler surface before installing/enabling that adapter. Do not silently substitute a high-level client with automatic approvals. |
| Dependency policy | Stable releases only; no global upgrades or prereleases. Record Python patch, package locks, Codex version, and generated protocol provenance before a live check. |

The [official OpenAI SDK documentation](https://learn.chatgpt.com/docs/codex-sdk) requires Python 3.10+ for the Python SDK and describes its bundled runtime pin. A compatible published SDK version has not yet been established locally. That is a gate for the real adapter, not a reason to guess a version or block the independent offline core.

## Input and classification defaults

Accept text prompts only initially. Ignore whitespace-only submissions without creating a coding turn. Otherwise preserve the exact submitted text and its UTF-8 SHA-256 hash. No conversation history, repository content/metadata, tools, previous failures, prior categories, link fetching, or summaries enter classifier task content. Fixed versioned category questions and definitions are the only additional classification instructions.

Limit the classifier's user-prompt portion to **16,384 UTF-8 bytes** initially. This is an application limit, not a claimed provider token limit. For larger text, skip classification and use fallback with reason `prompt_too_large`; preserve the full prompt for the executor. A real executor must separately validate its own input/context and budget limits. Do not silently truncate or summarize. Reject non-text/attachment inputs as `unsupported_input` without a model call; users may include code or error text directly in the prompt.

Use fixture taxonomy `draft-0` with these exact fields for the offline contract:

| Field | Values |
| --- | --- |
| `task_type` | `diagnose`, `fix`, `validate`, `mixed_or_unclear` |
| `cause_evidence` | `supporting_details`, `hypothesis_only`, `unknown` |
| `change_scope` | `localized`, `cross_component`, `unknown` |

These are implementation fixtures based on the current draft, not a frozen research taxonomy. Refinement requires a new taxonomy version and matching artifacts. `supporting_details` describes the prompt's contents, not verified root-cause correctness. Collect no training labels against an unreviewed taxonomy.

Default classifier deadline is **10 seconds total for the classification operation**, including all three fields. Automatic classifier retries: **zero**. Partial/malformed responses, unknown labels, timeout, or unavailable classifier lead to the configured fallback and a recorded reason. Unknown/mixed values are valid annotations but conservatively trigger fallback initially. Do not use an uncalibrated numerical confidence threshold; optional scores are diagnostics. A client timeout does not prove server computation stopped or cost was zero.

## Records and validation

Own application records use `schema_version: "0.1"`. Use opaque UUIDs, UTC ISO-8601 timestamps, monotonic elapsed milliseconds, nonnegative integer token counts or null, and decimal USD strings or null. Reject invalid required fields and unsupported schema versions at our boundary. Keep provider protocol parsing in its adapter; do not mistake these application fields for an existing SDK API.

| Record | Required content |
| --- | --- |
| Prompt | `prompt_id`, `session_id`, `turn_index`, `submitted_at`, `prompt_sha256`, `utf8_bytes`, `input_policy_version`; exact text held for execution, outside routine telemetry. |
| Classification | `classification_id`, `prompt_id`, `taxonomy_version`, `classifier_id`, nullable `classifier_revision`, `status`, nullable complete `labels`, nullable `scores`, `question_count`, `elapsed_ms`, nullable `error_code`, nullable `usage_id`. Status is `ok`, `skipped`, `invalid`, `timeout`, or `unavailable`. |
| Configuration | `configuration_id`, `provider`, `model_id`, `effort`, `supported_efforts`, `availability`, `is_fixture`, nullable documented `limits`, nullable dated `pricing`. Availability is `available`, `unavailable`, or `unverified`. |
| Policy decision | `decision_id`, `prompt_id`, nullable `classification_id`, `policy_version`, `mapping_version`, `eligible_configuration_ids`, nullable `selected_configuration_id`, `status`, nullable `reason`, nullable `reservation_id`. Status is `selected`, `fallback`, or `blocked`. |
| Usage | `usage_id`, `operation_id`, `source`, nullable provider request ID, nullable input/cached-input/output/reasoning token counts, nullable `estimated_cost_usd`, nullable `billed_cost_usd`, nullable `rate_version`, `elapsed_ms`, `status`. Source distinguishes `fixture`, provider observations, and estimates. |
| Run event | `event_id`, `run_id`, `session_id`, nullable `turn_id`, monotonic per-run `sequence`, `occurred_at`, `event_type`, `mode`, referenced record IDs, and event-specific data. |

All six records include the common schema version. Scores, if supplied, must be finite and within [0,1]; their availability is not required for routing. Missing usage is null/unavailable, never silently zero. Validate exact taxonomy membership and that a selected effort belongs to its model's supported set.

## Policy and accounting defaults

Use an explicit lookup from a complete `(task_type, cause_evidence, change_scope)` tuple to a configuration ID. Do not embed assumed model capabilities in application logic. A missing mapping, unknown/mixed signal, classifier error, or mapped configuration that is ineligible invokes one configured fallback. Validate that fallback independently. If it cannot run within availability and budget constraints, return `blocked`; do not walk an escalation chain.

Use clearly named fixture configurations `fixture.a.low`, `fixture.a.high`, `fixture.b.low`, and `fixture.b.high`. The offline fallback is `fixture.b.high`, solely an arbitrary simulation choice. Fixture mappings are supplied explicitly for verification and do not assert performance. Live mode must reject all fixture configurations. The real pool and reliable fallback will be selected through access checks and development measurements.

Default authorized external inference/cloud spend is **$0**. Loading credentials or merely having credits must not enable paid work. Future live batches require the reviewed estimate and explicit stage cap already agreed with the owner. The cumulative cloud ceiling remains strictly below $50; it is not a per-job authorization.

Implement reservations and decimal accounting against injected synthetic rates in offline checks. For later paid work, missing rates, unresolved prior usage, or inability to make a conservative reservation block new admissions. Deduplicate usage by operation/provider identifiers; cumulative snapshots replace their prior snapshot rather than being added again. Record cached/reasoning categories without automatically adding them to input/output totals. Keep billed dollars, estimates, credits, and cloud compute distinct. A cancelled or timed-out operation retains its unresolved reservation until reconciled.

## Session and control defaults

One active turn and at most one queued prompt per session. Further submissions receive a queue-full status; do not drop or overwrite prompts. Classify a queued prompt when it becomes the next admitted turn, using only its own text. Display classification labels, chosen model/effort or fixture IDs, fallback reason, and completion/error status; label unavailable cost rather than displaying a fabricated zero.

Model session states as `idle`, `classifying`, `running`, `waiting_for_approval`, `cancelling`, and `needs_reconciliation`. A terminal executor event returns the session to idle; task success still requires executable evaluation. Resume explicitly by stored session/thread ID and preserve the repository association. Do not create a new conversation silently if resumption fails. Store queued prompts only in memory initially; do not auto-replay queued work after restart.

Initial adapter-control defaults: **15-second initialization deadline**, **10-second control-request acknowledgement deadline**, and **15-minute wall-clock coding-turn deadline**, including approval waits. These are engineering limits for a later integration pilot, not fixed paper-evaluation limits. Cancellation during classification cancels that operation and prevents coding from starting, including after a late result. Cancellation or deadline expiry during coding requests one interrupt. If completion remains unconfirmed after 10 seconds, enter `needs_reconciliation`, stop queued work, and keep usage/reservations unresolved. An explicit cancellation pauses the queued prompt until the user resumes it. Never automatically resubmit a turn after an uncertain acknowledgement or stream failure.

Approval requests require an explicit response. Deny unknown requests or noninteractive approval attempts; preserve Codex's sandbox. No automatic approval, background privilege escalation, or change to global Codex settings. The [app-server documentation](https://learn.chatgpt.com/docs/app-server) describes start/resume, interruption, and terminal events; their exact version-matched payloads remain the real adapter's implementation gate.

Write append-only JSONL events under ignored `runs/`. Routine telemetry stores hashes and metadata, with raw prompt/tool content disabled. Optional raw artifacts, when explicitly needed, stay in ignored local storage. Logging failure blocks starting another operation that needs accounting. All fixture records carry `mode: "offline"` and cannot be mixed with measured experiment results.

## Tomorrow's starting point and later gates

On the next development session, prepare the isolated Python 3.12 environment and record its exact version, then build only the offline core defined here. Verify prompt isolation, configuration eligibility, fallback/blocked outcomes, bounded queue/cancellation/resume state, missing/duplicate usage, and truthful fixture labels. No real classifier endpoint, model inference, benchmark repository execution, or GPU job is needed for that slice.

Before the real executor: resolve and pin the compatible SDK/runtime, verify required approvals/control surfaces, and respect the previously declined account-inspection escalation. Before live calls: review the run estimate, access, limits, and cap. Before labels/benchmarks: finalize taxonomy/annotation, grouped manifests, isolation, and the first pilot. Before final claims: fix reliability/analysis, freeze the system, and run held-out evaluation. Completing this offline specification does not mark those later gates passed.

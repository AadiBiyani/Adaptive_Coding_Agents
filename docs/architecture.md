# Proposed architecture

Design baseline: October 25, 2026. The implementation has since added hosted classification, the terminal/Codex integration, and a localhost React frontend; the owner has verified one routed repair. See [HANDOFF](../HANDOFF.md) for current implementation and evidence. The research architecture below still includes future work. Deferred simulation code is archived locally. Follow the Jev-first [development plan](development-plan.md) and stop for owner review after every phase.

## Product and stack boundary

Build a dedicated terminal command around the Codex harness. “Like OpenRouter” means a single routing entry point that selects among supported model/effort configurations. A public hosted gateway, billing service, and full OpenAI-compatible API are outside the first product. The owner's October 29 request adds a localhost ChatGPT-style interface using JavaScript, React, and shadcn/ui. It calls the existing Python workflow through a local API, with no second coding client or duplicated policy. Its Spending tab only reprices observed tokens; it does not run a fixed baseline or replace matched benchmark evaluation.

The selected design uses Python for the initial terminal, routing policy, classifier clients, Codex app-server client, and run events, as well as task manifests, training, benchmarking, and analysis. Both interactive and benchmark entry points invoke the same coding execution path. The owner clarified that TypeScript was an earlier recommendation, not a required language.

Use candidate Python 3.12 environments managed with uv; pin compatible versions before setup. Keep GPU training/serving and benchmark evaluator dependencies separate despite sharing a language. Prefer the official Python app-server SDK if its pinned interface covers the required controls; otherwise assess a thin Python protocol adapter before implementation. TypeScript remains a fallback if a specific interface or maintenance advantage warrants it. Versioned JSON contracts and file artifacts suffice initially; no database or service framework is required. See [Research review](research-review.md) for the trade-off.

## Turn boundary

A user submits a new prompt. Once the preceding turn is complete, send only that prompt as Jev/OpenJev's dynamic task input, alongside fixed versioned category questions/definitions. It predicts a task type plus a few signals. A separate policy combines those labels with measured configuration performance, eligible settings, and remaining limits, then selects a GPT model and reasoning effort. Validate the route and start the Codex turn with explicit settings. Record the classification, policy decision, and observable execution separately.

Only new user prompts trigger routing. Internal model responses, tool calls, or failing tests during a turn do not trigger another route in the initial scope. New prompts received during execution are queued; cancellation is a separate explicit action. Do not treat a streamed message or `turn/steer` as a newly configured user turn.

The classifier input excludes history, repository metadata/content, tool results, previous failures, summaries, and inferred progress. User-pasted details within the current prompt are allowed; do not fetch referenced files or links to augment it. Keep runtime identifiers outside model-visible task content. The policy retains budget/availability information and measured development performance. Codex retains its conversation, repository access, and tools. Keep that coding context construction fixed across strategies and record compaction, switching, and cache effects. The classifier's limited view does not reset the coding session.

## Components

| Component | Language and responsibility |
| --- | --- |
| Terminal client | Python: prompt queue, routing display, streamed output, approvals, cancel/resume. |
| Local browser client | JavaScript/React/shadcn in `frontend/`: chat, file previews, token-price comparisons, and local test results. Python APIs and adapters live in `backend/src/`; both product surfaces share the same coding path. |
| Prompt encoder | Python: current prompt plus fixed category instructions; explicit input-size handling and no dynamic context enrichment. |
| Configuration registry | Shared validated data: models, efforts, execution limits, access state, and dated rates. |
| Classifier clients | Python: hosted Jev and OpenJev endpoints returning typed task categories/signals under one taxonomy contract. |
| Routing policy | Python: map classifications to model/effort using measured performance, eligibility, budgets, and fallback; also expose fixed/rule controls. |
| Codex client and recorder | Python: one pinned app-server session, execution events, errors, timing, and usage. |
| Benchmark runner | Python: task lifecycle, isolated execution, patch extraction, evaluator invocation, aggregation. |
| Training and analysis | Python: split/label audits, cheap learned baseline, OpenJev adapters, calibration, statistics. |

The cheap learned classifier produces the same category records and uses the same downstream policy as the Jev/OpenJev clients. A shared Python implementation avoids translating its feature extraction or decision logic into a second language. Retain process/environment isolation where dependencies require it.

## Codex integration

Use a version-pinned [app-server](https://learn.chatgpt.com/docs/app-server) using stdio JSON-RPC. It supplies the custom interactive workflow, approvals, and history we need. The [official Python SDK](https://learn.chatgpt.com/docs/codex-sdk) uses that server, retaining the Codex harness. Verify that the chosen distribution exposes the reviewed per-turn settings, approval responses, streaming, interruption, and resume controls, then validate behavior in the planned integration stage.

Phase 0 subsequently inspected the official Python source and selected a thin wrapper over the lower-level typed client with an explicit approval handler, subject to verifying the compatible published distribution. The convenience client's default accepts certain approvals and does not expose that handler through its high-level constructor. Follow the [source findings](technical-discovery.md#documented-codex-interface-candidates), preserve interactive approvals explicitly, and avoid modifying private SDK fields. No live behavior has been tested.

The inspected 0.164.0 schemas include `initialize`/`initialized`, `thread/start`, `thread/resume`, `turn/start` with `threadId`, `input`, `model`, and `effort`, and `turn/interrupt`. `model/list` is paginated and exposes supported reasoning efforts. Generate types from the version selected for implementation and use its exact enums and event shapes; do not copy incompatible current website examples blindly.

Support command, file-change, and permission approval requests through the documented protocol. Preserve Codex's normal tool and sandbox boundaries. The router chooses a configuration; Codex manages coding conversation, commands, edits, and tests. Unavailable or declined approvals must become visible outcomes, not silently authorized operations.

Live proof is still required: two user turns and resumption must preserve session/repository context while applying an observable model/effort change. Requested settings, API-accepted settings, and observable execution are separate records. Provider rerouting or unknown execution detail must remain explicit. Account inspection previously failed due to a local database write restriction and its escalation was declined; no access or billing assumption is justified by that attempt.

## Classifier and policy contract

The owner clarified the initial contract: Jev/OpenJev returns a task type plus a few categorical signals, and a separate routing policy chooses the configuration. This supersedes the earlier proposal to request a configuration ID directly from the classifier. Hosted Jev and OpenJev adapters share the same permitted task information and category definitions despite serialization differences. The [Phase 1 specification](phase-1-specification.md) records confirmed structure and provisional labels. A direct-selection ablation is optional later work.

Keep category questions independent of model IDs and prices; the policy receives registry/performance/budget data. Use a versioned category-to-configuration mapping, with its entries informed by measured development outcomes. Hold that mapping fixed in the primary untuned/tuned classifier comparison. Category supervision and configuration-outcome evidence have distinct provenance and purposes.

| Proposed record | Required meaning |
| --- | --- |
| Routing state | Schema version, task/session/turn IDs for tracking, current prompt and classifier-input hash/version; policy-only eligible configurations and remaining limits. IDs/history/repository state are not classifier features. |
| Classifier result | Requested/observed classifier version, taxonomy/question versions, task-type/signal labels or invalid result, optional per-question scores, latency, usage and cost provenance. |
| Policy decision | Consumed classification, mapping version, eligible configurations, selected configuration, fallback/rejection reason, budget reservation, links to state and classifier result. |
| Execution record | Codex thread/turn IDs, requested/accepted/observed settings, timestamps, completion/cancel/error reason, usage availability and artifact links. |

The current client uses provisional taxonomy `draft-1`, response records `jev-classification-1`, and prompt-only input policy `prompt-only-1`. It sends one request with three Choice questions to TypeSafe's System One endpoint and pins `jev-1.14.0`. Prompt text is capped at 16,384 UTF-8 bytes, rejected without truncation when oversized. Default preview prints the exact request; explicit live mode requires an API key. Response validation retains category scores, requested/returned model IDs, hashes, latency, and available usage, without inventing billing. Errors produce no labels and are not retried. See [the client](../backend/src/adaptive_coding_agents/jev.py) and [README](../README.md) for the implemented boundary. Current private coding records and local test records do not yet implement the complete benchmark contract below.

Option probability measures preference among category labels, not coding-task success. Do not use it as a claimed success probability. Keep a valid unknown/insufficient-evidence category distinct from malformed output, timeout, and unsupported policy routes. Define the handling of each before implementation and include every classifier question in cost and latency accounting.

## Configuration registry and execution limits

Record exact provider/model ID and immutable version when available, supported reasoning values, context/output limits, processing tier/mode, availability, pricing categories/source/date, and fallback eligibility. Do not assume low/high/off are portable settings. Log aliases and returned versions when an immutable model cannot be pinned.

The proposed pilot pool is `gpt-6-luna` and `gpt-6.1-sol`, each at `low` and `high`, pending account and Codex compatibility checks. The source-backed rationale is in [Research review](research-review.md#proposed-gpt-configurations); development results must choose a strong fixed baseline and fallback. No model is established as the best route for a task category.

Select eligible configurations before classification. All matched classifier/rule strategies share the prompt-only input boundary, allowed pool, per-task limits, and fallback policy; their coding agents share normal Codex context construction. Report strategy-specific overhead against the common total resource ceiling; do not give the classifier free extra attempts.

## Failure and budget behavior

The owner selected automatic reliable fallback for insufficiently informative prompts, without a router-only clarification question. Choose its exact configuration from development evidence and use it only when valid within remaining limits. Before implementation, also define failure/timeout rules, retries, deadlines, sparse categories, and unavailable configurations. If no valid choice fits, stop with a budget/availability outcome. Do not launch an unbounded escalation chain or enrich the classifier input to resolve an unknown. Normal Codex task questions and tool approvals remain part of the workflow.

Reserve for in-flight work and stop scheduling new calls at the configured limit. Provider billing can arrive late, and aggregate Codex usage may omit internal call details; describe caps as admission controls with documented accounting limits rather than guaranteeing an exact bill. Use exposed output/context limits to constrain exposure and reconcile provider records afterward.

Never record missing usage as zero. Distinguish measured tokens, actual billed amounts, dated price estimates, subscription quota, credit consumption, and cash costs. Deduplicate incremental/cumulative usage events. Include failed calls, retries, classifier inference, extra context and cache effects from switching. Hosted Jev, direct OpenAI coding calls, GPU hosting, and benchmark compute have separate billing paths.

## Benchmark execution boundary

Run benchmark repository commands and the coding agent's tools in the isolated environment selected for that benchmark. Hidden tests, reference patches, and unreleased later prompts remain in evaluator/controller storage outside the agent and router's accessible workspace. Regrade patches in clean environments using the pinned evaluator.

The Python controller prepares a task and starts the same Codex client path used by the terminal inside the permitted execution environment. It collects patches and records, then requests external evaluation. Each strategy/run has an independent repository and session; live adaptive outcomes cannot be manufactured from unrelated cached steps.

The detailed protocol is in [Evaluation](evaluation.md). Precise container images, credential delivery, evaluator revisions, and access boundaries must be specified before benchmark implementation; no benchmark code has been run on the developer's host.

## Design gate

Phase 1 ends with local tests and owner review of the direct Jev client and request preview. Phase 2 requires explicit instruction, TypeSafe account setup, and a reviewed estimate/cap before real classification and accuracy evaluation. Routing/CLI work follows Phase 2 review. Resolve compatible Codex client pins, configuration access, live caps, and benchmark isolation before dependent work. The planned architecture is not evidence of live behavior or performance.

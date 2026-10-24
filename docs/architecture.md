# Proposed architecture

Updated October 24, 2026. The requirements are agreed; the design below is a recommendation to review before implementation. The premature prototype was deleted. No live session integration, classifier adapter, or accounting implementation exists.

## Product and stack boundary

Build a dedicated terminal command around the Codex harness. “Like OpenRouter” means a single routing entry point that selects among supported model/effort configurations. A public hosted gateway, billing service, dashboard, and full OpenAI-compatible API are outside the first product.

Use TypeScript in strict mode for the terminal, routing policy, classifier clients, Codex app-server client, and run events. Use Python for task manifests, benchmark orchestration, label construction, OpenJev training, and analysis. The Python runner invokes the same TypeScript coding execution path that the interactive terminal uses; it does not implement a different agent loop.

Recommended tooling is Node.js 24 LTS with npm and candidate Python 3.12 environments with uv. Pin exact compatible versions before setup. Keep GPU training/serving and benchmark evaluator dependencies in separate environments. A small TypeScript package, versioned JSON contracts, and file-based artifacts are enough initially; no database or service framework is required. The rationale and sources are in [Research review](research-review.md).

## Turn boundary

A user submits a new prompt. Once the preceding turn is complete, capture that prompt and a bounded snapshot of information already available, form the eligible configuration list, classify the state, validate the choice, and start a Codex turn with explicit model and effort. Record the decision and observable execution settings.

Only new user prompts trigger routing. Internal model responses, tool calls, or failing tests during a turn do not trigger another route in the initial scope. New prompts received during execution are queued; cancellation is a separate explicit action. Do not treat a streamed message or `turn/steer` as a newly configured user turn.

Later routing states may include previous visible failures, progress, and remaining limits. Keep the context-selection and handoff rules fixed across strategies. Prefer deterministic selection/truncation first: a paid summarizer would add cost and another experimental variable. Record any Codex compaction, model-switch instruction, or cache behavior that changes effective context and overhead.

## Components

| Component | Language and responsibility |
| --- | --- |
| Terminal client | TypeScript: prompt queue, routing display, streamed output, approvals, cancel/resume. |
| Context builder | TypeScript: bounded decision-time snapshot with explicit permitted sources and truncation. |
| Configuration registry | TypeScript/shared data: valid models, efforts, execution limits, access state, and dated rates. |
| Classifier clients | TypeScript: hosted Jev and OpenJev endpoints behind one typed decision contract. |
| Routing policy | TypeScript: fixed, rules, learned/classifier decisions, deterministic eligibility and fallback. |
| Codex client and recorder | TypeScript: one pinned app-server session, execution events, errors, timing, and usage. |
| Benchmark runner | Python: task lifecycle, isolated execution, patch extraction, evaluator invocation, aggregation. |
| Training and analysis | Python: split/label audits, cheap learned baseline, OpenJev adapters, calibration, statistics. |

The cheap learned policy must be invocable through the same routing interface. Choose a small portable representation or a narrow local process boundary when its model is selected; do not duplicate policy logic in two languages.

## Codex integration

Recommend a version-pinned [app-server](https://learn.chatgpt.com/docs/app-server) using stdio JSON-RPC. It supports the custom interactive workflow, approvals, and history we need. The SDK is another supported automation interface, but using app-server for both the product and benchmark client avoids introducing a second execution path.

The inspected 0.164.0 schemas include `initialize`/`initialized`, `thread/start`, `thread/resume`, `turn/start` with `threadId`, `input`, `model`, and `effort`, and `turn/interrupt`. `model/list` is paginated and exposes supported reasoning efforts. Generate types from the version selected for implementation and use its exact enums and event shapes; do not copy incompatible current website examples blindly.

Support command, file-change, and permission approval requests through the documented protocol. Preserve Codex's normal tool and sandbox boundaries. The router chooses a configuration; Codex manages coding conversation, commands, edits, and tests. Unavailable or declined approvals must become visible outcomes, not silently authorized operations.

Live proof is still required: two user turns and resumption must preserve session/repository context while applying an observable model/effort change. Requested settings, API-accepted settings, and observable execution are separate records. Provider rerouting or unknown execution detail must remain explicit. Account inspection previously failed due to a local database write restriction and its escalation was declined; no access or billing assumption is justified by that attempt.

## Classifier and policy contract

The proposed first contract is a typed choice of one eligible configuration ID, not free-form model names or an explanatory chain of thought. Hosted Jev and OpenJev adapters may serialize differently, but receive the same allowed state and candidate information. Direct choice versus feature classification is a later optional experiment; keep the adapter/policy boundary separate without implementing both now.

| Proposed record | Required meaning |
| --- | --- |
| Routing state | Schema version, task/session/turn IDs, current prompt, bounded visible context/progress, context-selection version/hash, eligible configurations, remaining limits. |
| Classifier result | Requested/observed classifier version, chosen configuration ID or invalid result, optional option scores, latency, usage and cost provenance. |
| Policy decision | Requested choice, final eligible configuration, policy version, fallback/rejection reason, budget reservation, links to state and classifier result. |
| Execution record | Codex thread/turn IDs, requested/accepted/observed settings, timestamps, completion/cancel/error reason, usage availability and artifact links. |

Define one versioned JSON Schema contract shared with the Python runner. Exact field names, truncation limits, deadlines, and fallback values remain Phase 1 decisions. JSONL event logs and hashed manifests provide the initial storage boundary; add Parquet only if analysis benefits.

Option probability measures the classifier's preference among choices. It is not automatically the probability that the coding task will pass. Do not route based on a claimed success confidence without development calibration and validation. Invalid output, timeout, or unsupported configuration follows a predeclared deterministic fallback.

## Configuration registry and execution limits

Record exact provider/model ID and immutable version when available, supported reasoning values, context/output limits, processing tier/mode, availability, pricing categories/source/date, and fallback eligibility. Do not assume low/high/off are portable settings. Log aliases and returned versions when an immutable model cannot be pinned.

The proposed pilot pool is `gpt-6-luna` and `gpt-6.1-sol`, each at `low` and `high`, pending account and Codex compatibility checks. The source-backed rationale is in [Research review](research-review.md#proposed-gpt-configurations); development results must choose a strong fixed baseline and fallback. No model is established as the best route for a task category.

Select eligible configurations before classification. All strategies share the allowed pool, context information, per-task limits, and fallback policy. Report strategy-specific overhead against the common total resource ceiling; do not give the classifier free extra attempts.

## Failure and budget behavior

Before implementation, choose a valid fallback for classifier failure, maximum retries, deadlines, and policy for unavailable configurations. Prefer the development-selected reliable fallback when it fits remaining limits. If no valid choice fits, stop with a budget/availability outcome. Do not launch an unbounded escalation chain.

Reserve for in-flight work and stop scheduling new calls at the configured limit. Provider billing can arrive late, and aggregate Codex usage may omit internal call details; describe caps as admission controls with documented accounting limits rather than guaranteeing an exact bill. Use exposed output/context limits to constrain exposure and reconcile provider records afterward.

Never record missing usage as zero. Distinguish measured tokens, actual billed amounts, dated price estimates, subscription quota, credit consumption, and cash costs. Deduplicate incremental/cumulative usage events. Include failed calls, retries, classifier inference, extra context and cache effects from switching. Hosted Jev, direct OpenAI coding calls, GPU hosting, and benchmark compute have separate billing paths.

## Benchmark execution boundary

Run benchmark repository commands and the coding agent's tools in the isolated environment selected for that benchmark. Hidden tests, reference patches, and unreleased later prompts remain in evaluator/controller storage outside the agent and router's accessible workspace. Regrade patches in clean environments using the pinned evaluator.

The Python controller prepares a task and starts the same TypeScript/Codex path inside the permitted execution environment. It collects patches and records, then requests external evaluation. Each strategy/run has an independent repository and session; live adaptive outcomes cannot be manufactured from unrelated cached steps.

The detailed protocol is in [Evaluation](evaluation.md). Precise container images, credential delivery, evaluator revisions, and access boundaries must be specified before benchmark implementation; no benchmark code has been run on the developer's host.

## Design gate

Before coding, resolve the terminal state transitions, exact shared records, context cap, configuration/fallback behavior, timeout/retry/budget limits, and benchmark isolation plan. Record choices in the master [Development plan](development-plan.md). Live validation follows as a small purposeful experiment after the design is clear; the architecture itself is not evidence of implementation.

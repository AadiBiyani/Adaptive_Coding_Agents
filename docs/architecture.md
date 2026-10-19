# Proposed architecture

The agreed behavior is per-user-prompt selection of a GPT model and reasoning effort while preserving a Codex coding session. The component boundaries below are a proposed implementation plan. No runtime interface has been implemented or validated yet.

## Turn boundary

At the beginning of a new user turn, capture the prompt and a bounded snapshot of available conversation and repository context. On later turns, that snapshot can include previous visible failures or progress. Classify that state, choose an eligible configuration, validate the choice against supported settings and remaining limits, and start the Codex turn. Record the decision and actual execution settings.

Candidate signals from the original proposal include investigation/implementation/validation phase, unresolved diagnosis, reasoning across several components, visible test failures, progress across previous attempts, and remaining time/spending budget. These signals and their routing effects need measurement; the examples in [Research hypotheses and extensions](research-notes.md) are hypotheses rather than a validated rule set.

After the turn starts, allow the coding harness to manage tool use, edits, and tests. Internal test failures do not themselves trigger a fresh routing decision in the initial scope. A subsequent user prompt does. Preserve a stable handoff/context format across model changes so experiments measure routing rather than changing summarization strategies.

## Components

| Component | Responsibility |
| --- | --- |
| Terminal client | Receive prompts, display output, preserve interactive task/session behavior |
| Context builder | Produce bounded decision-time inputs without hidden checks or future outcomes |
| Classifier adapter | Offer a common interface for hosted Jev, untuned OpenJev, and tuned OpenJev |
| Routing policy | Select a configuration from classifier signals and measured development performance |
| Configuration registry | List exact model IDs, supported effort controls, and other execution settings |
| Codex adapter | Apply the selected configuration to a turn and retain conversation/repository continuity |
| Run recorder | Associate routing, usage, outputs, and failures with reproducible task/run/turn IDs |
| Benchmark runner | Execute strategies with matched conditions and call the external task evaluator |

## Codex integration

The owner accepts a dedicated terminal command. A Codex app-server client is the candidate integration identified during planning, because session continuity and per-turn configuration control are the key needs. Before choosing it, inspect the installed version and current official documentation and run a small integration spike. No claim is made that the stock terminal UI already exposes the required router hook.

The spike must demonstrate two user turns in one task session, an observable change in the requested and actually used model/effort settings, preserved repository context, and ordinary tool/approval behavior. An offline stub can validate the client's orchestration first; verifying real model behavior requires a bounded authorized live check.

The router supplies decisions, not an alternative tool executor. Preserve the coding harness's normal execution boundaries. If a chosen integration cannot honor a setting, surface and log that limitation rather than silently pretending it was applied.

## Classifier and policy contract

Keep the model classifier and route policy separate so both direct configuration selection and classification-followed-by-policy can be studied later. The first implementation only needs one consistent decision contract. The exact output labels, confidence use, training objective, and prompt template are open decisions.

A proposed decision record includes the input/context reference, classifier and policy versions, selected configuration ID, decision latency, classifier usage/cost, and whether fallback was used. Do not require hidden chain-of-thought. Optional confidence scores need outcome-based calibration before they can be treated as probabilities of success.

The configuration registry should record provider, model ID/version where available, supported reasoning controls, selected effort or token budget, output limits, availability, and pricing reference/date. Do not let a classifier invent model names or unsupported settings. GPT coding execution and classifier hosting may use different services; access through one platform does not establish that the owner's GPT credits cover another platform's charges.

## Failure and budget behavior

Define a fixed eligible fallback for timeouts, invalid classification output, or unavailable choices before the pilot. Cap retries and log every attempted call. If no eligible configuration fits the remaining limits, stop with a recorded budget/availability outcome. Do not turn fallback into an uncontrolled series of increasingly expensive attempts.

Distinguish requested configuration, accepted configuration, and any observable executed model/settings. Report unknown information as unknown. Budget checks and usage estimates cannot guarantee exact billing when a provider delays final usage; reconcile usage records after the run.

## Candidate code layout

Choose a language/runtime after the integration spike. The names below describe future responsibilities, not existing modules or a committed framework choice:

```text
src/             terminal client, Codex adapter, context builder, router, classifier adapters
configs/         reviewed configuration and experiment definitions without secrets
benchmarks/      task manifests, split definitions, runner and evaluation adapters
training/        development-example construction and OpenJev fine-tuning workflow
tests/           offline checks plus explicitly opt-in integration checks
results/         small reviewed aggregate reports and reproduction metadata
```

Do not create empty implementation scaffolding merely to imply these components already exist.

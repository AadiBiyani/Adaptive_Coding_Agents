# Development handoff

Updated October 24, 2026 after the owner selected conservative defaults and said development would begin tomorrow. Read this file, then the project brief, architecture, evaluation, and development plan before continuing.

## Current instruction and state

The owner explicitly asked to delete the code written prematurely, set Milestone 2 aside, and review the product/research plan before coding. Phase 0's requirements/discovery review is complete. The owner has now delegated conservative engineering defaults and said development will start tomorrow. **The first offline build contract is ready in `docs/first-build-defaults.md`; do not start coding tonight or run unattended work. On the next resumed development session, begin that bounded offline slice.** Broader Phase 1 research/live-integration decisions retain their stage-specific gates in `docs/phase-1-specification.md`. `docs/development-plan.md` is the primary roadmap; the milestone plan is an inactive course reference.

The premature JavaScript prototype had already been moved into `build/deferred-javascript-20261024/`. That archive and its integrity manifest, generated files in `build/codex-schema/`, and the empty source/test/config/build directories were deleted at the owner's request. No application source, package manifest, tests, dependency installation, or generated protocol files remain. Do not restore the archive or treat it as accepted implementation.

The earlier prototype's offline checks and simulated demo were not live product or research results. No actual coding-model inference, benchmark run, training job, tuned checkpoint, or measured routing gain has been established. This review changed planning documents only and launched no paid experiments.

Selected defaults: Python 3.12 in an isolated uv environment, standard-library offline core and checks, explicit fixture classifier/executor, versioned records, 16 KiB classifier prompt limit with unchanged-prompt fallback for oversize text, three draft category fields, zero automatic retries, one active/one queued turn, explicit approvals, conservative cancellation/reconciliation, JSONL events under ignored `runs/`, and $0 authorized external spend. Fixture fallback is `fixture.b.high`, not a real-model recommendation. See the defaults document for exact fields, timeouts, and error behavior.

## Goal and confirmed scope

Build a dedicated terminal command that preserves the Codex coding workflow and session context. For each newly submitted user prompt, Jev/OpenJev receives only that specific prompt as dynamic task content, plus fixed category instructions, and classifies a task type plus a few signals. Exclude added history, summaries, repository contents/metadata, tool results, and prior failures. A separate policy uses the labels, measured performance, available configurations, and remaining limits to choose a supported GPT model and reasoning effort. Codex retains its normal session context. These owner clarifications supersede direct configuration choice and the earlier context-enriched classifier proposal. Route at user-message boundaries, not internal tool/model steps. Start with bug fixing/debugging.

The primary research question is whether fine-tuning OpenJev improves routing over untuned OpenJev, producing better task performance or lower cost/token usage. Hold the taxonomy and downstream mapping fixed in that matched comparison. Deliver it alongside hosted TypeSafe Jev, strong fixed configurations, simple rules, and a cheap learned category-classifier control. Category annotations supervise classifier adaptation; separate measured configuration outcomes establish the policy. Keep SWE-bench, a controlled multi-turn evaluation, and qualitative stakeholder feedback; multi-turn adaptation is secondary. Correctness comes first; savings and productivity gains remain hypotheses.

The owner clarified that TypeScript was an earlier agent recommendation, not a personal requirement. Stack selection is open to the best supported fit; do not misattribute the two-language design to the owner. Fine-tuning remains required; do not silently replace it with a rules-only product or a different similarly named model. “Like OpenRouter” means a routing entry point and interchangeable configurations, not an entire public gateway business.

During the Phase 0 question-and-answer review, the owner confirmed research/personal testing first and Python repositories for the initial training/benchmark cohort. The current checkpoint's terms still need to be respected, and commercial/workplace deployment is a later decision. The owner believes a Linux server is available; access, hardware, containers, and quotas remain unverified. No free GPU allocation is confirmed. The primary question and all current Phase 0 questions have been answered.

The owner reports **$3,333 in OpenAI API credits**, superseding the earlier $3,000 estimate, and wants minimal consumption for necessary validation, submissions, or ML-paper experiments. Balance, expiry, eligible models, and billing access remain unverified. The credits are not a spending target or authorization. Cloud spending must stay strictly under $50 cumulatively; conservatively include other non-OpenAI cash costs until separately reviewed. The owner will set the API cap after reviewing a run-by-run estimate; no preset $10/$25 allowance was accepted. No paid experiment or GPU provision has been authorized for execution.

The owner confirmed the Phase 1 output structure as task type plus a few signals. Draft fields are task type, cause evidence described in the prompt, and expected change scope, with exact values still provisional. Those labels must describe only the current prompt, including unknowns when evidence is absent. The owner selected automatic reliable fallback for ambiguous prompts such as “try again,” within remaining limits, without router-only clarification. The exact fallback configuration is still to be selected from development evidence. OpenJev performs work per question, so multiple fields must be counted in latency and cost.

The owner then asked whether extra context would be worthwhile. The recommendation is prompt-only for the first study, with a separately scoped context comparison if the development pilot exposes missing-information limits. This is a recommendation, not a new owner decision to add context. Do not silently enrich inputs. Fallback frequency/cost may offset classifier savings, and fine-tuning cannot recover missing facts. See `docs/phase-1-specification.md` for the proposed later experiment.

## Findings and recommended design

- Select Python for the initial terminal/router and research tooling, with one version-pinned Codex app-server execution path. This reduces duplicated policy/data logic compared with the earlier TypeScript/Python split. Official source inspection supports a lower-level typed Python client with an explicit approval handler; the high-level convenience constructor does not expose that handler and its default accepts certain approvals. Verify the compatible published distribution before implementing/enabling the real adapter; the independent offline core needs no SDK dependency. Preserve interactive approvals and do not patch private fields. No implementation has begun.
- Read-only environment checks tonight reported default `python3` 3.9.6, uv 0.11.16, and Codex CLI 0.164.0. Use an isolated Python 3.12 environment during the next session; record the exact patch then. No environment was installed and no app-server/account inspection was attempted.
- Local CLI inspection reported `codex-cli 0.164.0`. Generated schemas were inspected before deletion and included per-turn `model`/`effort`, thread start/resume, paginated model discovery, approvals, interruption, and usage. Live continuity/configuration execution and full billing observability remain unproved.
- The previous account/model inspection attempt could not initialize Codex's local SQLite state because of filesystem restrictions. The owner declined the escalation. Do not retry it or work around the denial without renewed authorization.
- A proposed pilot grid is `gpt-6-luna` and `gpt-6.1-sol` at low/high effort, subject to actual access and Codex compatibility. Official catalog support is not account access or a measured best model.
- The reviewed `openjev/openjev` is an independent 27B checkpoint. The pinned helper was retrieved with permission for public-source reading, inspected without execution, and hash-verified. Its text option-token readout is documented in the training plan. Adapter/readout compatibility and a capped memory/backward-pass check remain necessary. Supervised option-token LoRA is proposed; QLoRA is conditional. Public-source download permission did not renew the declined account-inspection permission.
- Prior work already covers coding routing, effort routing, and Jev-based decisions. A narrower executable empirical study is more defensible than claiming these ideas are new. Fine-tuning economics and simple learned controls matter.
- Start with a small pinned SWE-bench Verified development pilot, excluding its tasks and derivatives from held-out use. Ordinary issue-to-patch evaluation tests initial routing; claims about adaptation across user prompts require the separate multi-turn protocol. Final cohort/version, numeric reliability margin, sample size, and execution environment remain to be specified and validated.

Phase 0 is complete at the requirements/discovery level. These source findings and design choices do not establish live integration, GPU training fit, or research gains. Details and primary sources are in the files below.

## Files in play

| File | Role |
| --- | --- |
| `README.md` | Project orientation and current status. |
| `AGENTS.md` | Persistent scope, work, cost, and repository rules. |
| `docs/development-plan.md` | Primary phased roadmap, design gates, and decision ledger. |
| `docs/project-brief.md` | Development summary of the agreed need and current resources. |
| `docs/architecture.md` | Proposed Python-first design, Codex integration, contracts, and limits. |
| `docs/phase-0-decisions.md` | Completed Phase 0 answers, selected design, source checks, and later validation gates. |
| `docs/phase-1-specification.md` | Active category/policy specification, provisional labels, training evidence, and remaining contracts. |
| `docs/first-build-defaults.md` | Selected offline-build contracts, runtime approach, record fields, limits, fallback, and state/accounting defaults. |
| `docs/evaluation.md` | Controls, SWE-bench/multi-turn design, splits, statistics, costs, and records. |
| `docs/training-plan.md` | OpenJev identity, proposed labels/adapter loop, compatibility gate, and provenance. |
| `docs/research-review.md` | Dated primary-source review, technology/model candidates, and related-work overlap. |
| `docs/technical-discovery.md` | Local/protocol evidence, attempted inspection, and remaining live checks. |
| `docs/research-notes.md` | Original hypotheses and optional extensions; does not override current scope. |
| `docs/milestone-2-plan.md` | Inactive course requirements and historical ten-day proposal. |
| `docs/context-sources.md` | Context provenance and privacy boundaries. |

## Next unfinished work

Tomorrow/next resumed development session: follow `docs/first-build-defaults.md`, prepare the isolated Python environment, and implement the offline records, prompt encoder, registry/policy validation, fallback, event/accounting path, and simulated execution. Use meaningful offline checks and label every result as a fixture. Do not reopen settled product decisions or demand final research results before building this independent core.

Before enabling real adapters/calls, verify exact SDK/runtime pins, access, pricing, budgets, and a reviewed run estimate. Before collecting training labels or running benchmarks, settle the research taxonomy/annotation quality, shared measured mapping, real fallback, grouped manifests, and isolated environment. Numerical reliability criteria and final-study precision must be fixed before held-out evaluation. These later gates are not marked complete by the offline defaults.

Keep design choices separate from empirical checks. Once the relevant design is clear and implementation is requested, the first coding slice is a fixed/stub session client with offline verification, followed by a separately capped live proof. Then build the evaluator and fixed pilot, add classifier controls, collect category annotations and configuration outcomes, fine-tune, freeze, and evaluate. Do not begin with GPU rental or a large benchmark sweep.

## Historical context and private material

The Milestone 1 proposal and private submission ZIP were finalized in September; the owner confirmed the attestations and corrected agreement authorization. Upload/grading was not established by that structural check. The exact approved brief and stakeholder evidence stay in the private course workspace. No new stakeholder review or feedback has been conducted by the agent.

The owner pasted the original broader proposal on October 19 after the linked private chat could not be read. Its optional internal-checkpoint experiments do not replace the later user-prompt scope. On October 24 the course Milestone 2 package was inspected, but its schedule has now been explicitly set aside. Its packaging rules do not govern product development.

Keep personal contact details, student identifiers, private conversations/evidence, secrets, and employer material out of Git. No access to a stakeholder's former employer's repositories or benchmark is assumed. Keep this handoff sufficient for a fresh clone; a local memory service is not required.

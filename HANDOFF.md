# Development handoff

Updated October 24, 2026 after the owner requested a return to requirements and research planning. Read this file, then the project brief, architecture, evaluation, and development plan before continuing.

## Current instruction and state

The owner explicitly asked to delete the code written prematurely, set Milestone 2 aside, and review the full product/research plan before writing more code. **Continue planning; do not start another prototype while the current design choices remain unresolved.** `docs/development-plan.md` is the primary roadmap. `docs/milestone-2-plan.md` is an inactive course reference, not the development schedule.

The premature JavaScript prototype had already been moved into `build/deferred-javascript-20261024/`. That archive and its integrity manifest, generated files in `build/codex-schema/`, and the empty source/test/config/build directories were deleted at the owner's request. No application source, package manifest, tests, dependency installation, or generated protocol files remain. Do not restore the archive or treat it as accepted implementation.

The earlier prototype's offline checks and simulated demo were not live product or research results. No actual coding-model inference, benchmark run, training job, tuned checkpoint, or measured routing gain has been established. This review changed planning documents only and launched no paid experiments.

## Goal and confirmed scope

Build a dedicated terminal command that preserves the Codex coding workflow and session context. Before each newly submitted user prompt, choose both a supported GPT model and reasoning effort from a registry. Route at user-message boundaries, not at internal tool/model steps. Start with bug fixing/debugging.

Deliver hosted TypeSafe Jev, untuned independent OpenJev, and fine-tuned OpenJev comparisons alongside strong fixed and simple-rule controls. Add a cheap learned baseline for the paper study. Keep SWE-bench, a controlled multi-turn evaluation, and qualitative stakeholder feedback. Correctness comes first; savings and productivity gains remain hypotheses.

The owner reaffirmed TypeScript for the terminal/router/Codex client and Python for training, benchmark orchestration, and analysis. Fine-tuning remains required; do not silently replace it with a rules-only product or a different similarly named model. “Like OpenRouter” means a routing entry point and interchangeable configurations, not an entire public gateway business.

The owner reports **$3,333 in OpenAI API credits**, superseding the earlier $3,000 estimate, and wants minimal consumption for necessary validation, submissions, or ML-paper experiments. Balance, expiry, eligible models, and billing access remain unverified. The credits are not a spending target or authorization. API stage limits and separate classifier/cloud/benchmark cash caps are undecided. No paid experiment or GPU provision is authorized.

## Findings and recommended design

- Use one version-pinned Codex app-server stdio client in TypeScript for interactive and benchmark execution. Node.js 24 LTS/npm and Python 3.12/uv are recommended runtime choices; exact compatible pins remain to be selected.
- Local CLI inspection reported `codex-cli 0.164.0`. Generated schemas were inspected before deletion and included per-turn `model`/`effort`, thread start/resume, paginated model discovery, approvals, interruption, and usage. Live continuity/configuration execution and full billing observability remain unproved.
- The previous account/model inspection attempt could not initialize Codex's local SQLite state because of filesystem restrictions. The owner declined the escalation. Do not retry it or work around the denial without renewed authorization.
- A proposed pilot grid is `gpt-6-luna` and `gpt-6.1-sol` at low/high effort, subject to actual access and Codex compatibility. Official catalog support is not account access or a measured best model.
- The reviewed `openjev/openjev` is an independent 27B checkpoint. The serving recipe does not prove a fine-tuning recipe or training fit. Exact pinned helper inspection, adapter/readout compatibility, and a capped memory/backward-pass check remain necessary. Supervised option-token LoRA is proposed; QLoRA is conditional.
- Prior work already covers coding routing, effort routing, and Jev-based decisions. A narrower executable empirical study is more defensible than claiming these ideas are new. Fine-tuning economics and simple learned controls matter.
- Ordinary SWE-bench issue-to-patch evaluation tests initial routing. Claims about adaptation across user prompts require the separate multi-turn protocol. Final cohort/version, numeric reliability margin, sample size, and compute remain open.

These are planning findings and recommendations, not completed phases. Details and primary sources are in the files below.

## Files in play

| File | Role |
| --- | --- |
| `README.md` | Project orientation and current status. |
| `AGENTS.md` | Persistent scope, work, cost, and repository rules. |
| `docs/development-plan.md` | Primary phased roadmap, design gates, and decision ledger. |
| `docs/project-brief.md` | Development summary of the agreed need and current resources. |
| `docs/architecture.md` | Proposed TypeScript/Python boundary, Codex integration, contracts, and limits. |
| `docs/evaluation.md` | Controls, SWE-bench/multi-turn design, splits, statistics, costs, and records. |
| `docs/training-plan.md` | OpenJev identity, proposed labels/adapter loop, compatibility gate, and provenance. |
| `docs/research-review.md` | Dated primary-source review, technology/model candidates, and related-work overlap. |
| `docs/technical-discovery.md` | Local/protocol evidence, attempted inspection, and remaining live checks. |
| `docs/research-notes.md` | Original hypotheses and optional extensions; does not override current scope. |
| `docs/milestone-2-plan.md` | Inactive course requirements and historical ten-day proposal. |
| `docs/context-sources.md` | Context provenance and privacy boundaries. |

## Next unfinished work

Finish Phase 0's design review and Phase 1's concrete specifications. Review the app-server state/approval/usage contract; inspect the pinned OpenJev helper/readout; choose the initial benchmark/environment and split strategy; and settle context limits, fallback, timeouts, retry behavior, and resource accounting. Numerical reliability criteria and final-study precision must be fixed before held-out evaluation, using stakeholder needs and development evidence.

Keep design choices separate from empirical checks. Once the relevant design is clear and implementation is requested, the first coding slice is a fixed/stub session client with offline verification, followed by a separately capped live proof. Then build the evaluator and fixed pilot, add classifier controls, collect outcome labels, fine-tune, freeze, and evaluate. Do not begin with GPU rental or a large benchmark sweep.

## Historical context and private material

The Milestone 1 proposal and private submission ZIP were finalized in September; the owner confirmed the attestations and corrected agreement authorization. Upload/grading was not established by that structural check. The exact approved brief and stakeholder evidence stay in the private course workspace. No new stakeholder review or feedback has been conducted by the agent.

The owner pasted the original broader proposal on October 19 after the linked private chat could not be read. Its optional internal-checkpoint experiments do not replace the later user-prompt scope. On October 24 the course Milestone 2 package was inspected, but its schedule has now been explicitly set aside. Its packaging rules do not govern product development.

Keep personal contact details, student identifiers, private conversations/evidence, secrets, and employer material out of Git. No access to a stakeholder's former employer's repositories or benchmark is assumed. Keep this handoff sufficient for a fresh clone; a local memory service is not required.

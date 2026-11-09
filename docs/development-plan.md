# Jev-first development plan

Updated October 30, 2026. This roadmap supersedes the earlier fixture-first sequence and inactive course schedule. **Stop after every phase for owner testing and code review. Begin the next phase only after explicit instruction.** Within later phases, deliver small reviewable slices; phase approval does not authorize unestimated spending. The owner runs all commands that consume tokens or money.

**Latest owner direction:** finish the demo's per-chat, shared-spending, and experiment controls, then stop development for Ryan's review and feedback. This supersedes the earlier instruction to continue directly through Parts 3–5. Parts 1–2 code and the local React/shadcn interface are implemented. The classifier pilot supports human label review, separate development/held-out runs, and spending confirmation; real accuracy results remain pending. The demo now gives each chat 10 user turns, preserves cumulative dollar caps across chats, and gives experiments separate request quotas. See [HANDOFF](../HANDOFF.md) for verification and manual checks. Resume only on the owner's instruction after feedback; Part 3's development-measured policy, Part 4's SWE-bench comparison, Part 5's repeatable review material, and untuned/fine-tuned OpenJev remain future work. This does not retroactively complete Phase 2.

The latest UI refinement keeps software regression checks in the terminal and renames the research page Evaluation. Chat now displays Jev's per-category probabilities and the separate policy's model/effort explanation on every turn. These summaries are stored in the shared workflow for later multi-turn analysis. Neither the classifier pilot nor these displays establish measured routing quality or complete Parts 3–5.

## Phase 1 — Repository cleanup and direct Jev client

Preserve deferred code in an ignored verified archive. Remove simulated CLI/routing/execution components from the active package; retain prompt/category validation and Python packaging. Keep tests local and ignored. Show current and planned components in a GitHub-rendered README diagram.

Implement direct hosted TypeSafe Jev classification through the documented System One API. Use only the current prompt plus fixed category questions/definitions, with no context enrichment. Start with the existing three category fields, explicit provisional definitions, and pinned `jev-1.14.0`. Preview requests by default; live mode requires an explicit flag and API key. Reject oversize input unchanged, validate responses, preserve unknowns and missing usage, and report failures without automatic retries or invented predictions.

**Owner checkpoint:** inspect the code and request preview, run the local network-free tests, and review README architecture. Live inference is not validated by these checks. No accounts, calls, purchases, benchmarks, or training in this phase. General setup is in [README](../README.md#getting-started); current review commands are in [HANDOFF](../HANDOFF.md#manual-review).

## Phase 2 — Real Jev classification and accuracy

**Current checkpoint:** Phase 1 and the recording slice are reviewed, and real Jev responses are recorded. The 20-development/20-held-out diagnostic dataset, accuracy runner, and browser review/confirmation flow are implemented, but labels await human review and no accuracy batch has run. The reviewed cumulative allocation remains $0.05 Jev and $2 OpenAI. The owner authorized replacing the old global 43-request/three-turn limit with a per-chat allowance (demo default: 10 user turns), plus 40 Jev requests and zero coding turns allocated to `classifier-pilot`. Both use the same dollar ledger; existing charges are preserved. A new chat resets only that chat's turn allowance. The owner sends live messages and confirms any classifier batch. Do not add unreviewed retries, new allocations, or repeated experiments.

After Phase 1 review and explicit instruction:

1. Set up the direct TypeSafe account; verify access, actual credit/top-up requirements, and current pricing. OpenAI credits cannot pay this provider.
2. Present a run-by-run estimate and obtain the owner's API spending cap. Begin with one real request and inspect model identity, all three answers, usage, and failure reporting.
3. Prepare realistic Python debugging prompts with independent prompt-only human labels. Include code, tracebacks, reproduction details, vague follow-ups, mixed requests, and unknown scope. These are research examples, distinct from mocked unit tests.
4. Refine the taxonomy on training/development examples; group related prompts and freeze definitions before held-out evaluation. Preserve ambiguity and review provenance. Do not use predictions as their own gold labels.
5. Implement the small accuracy runner and report per-field accuracy/macro-F1, all-fields exact match, confusion matrices, unknowns, failures, latency, and usage. Include attempted failures in reporting and keep billed amounts separate from estimates. Run only the approved batch.

**Owner checkpoint:** review real responses, labels, evaluation code, and measured results. Classifier agreement does not establish coding success or routing savings. Stop before routing/CLI development.

## Phase 3 — Routing, Codex terminal workflow, and research evaluation

After Phase 2 review and explicit instruction, selectively reuse archived components where justified. Establish a supported GPT configuration registry and separate policy informed by measured development outcomes. Use an eligible fallback for ambiguous prompts; do not add context or router-only clarification questions.

Verify a version-compatible Codex interface, preserve approvals and conversation continuity, and use one coding execution path for terminal and benchmark runs. Test integration offline before a separately approved live check. Then deliver the terminal command and isolated executable evaluator in small reviewable slices. No new coding harness or automatic restoration of the old prototype.

Retain the full research deliverables:

- SWE-bench patch evaluation, competitive fixed/rules/cheap learned controls, and a small controlled multi-turn study.
- Hosted Jev, untuned OpenJev, and fine-tuned OpenJev; hold taxonomy and downstream policy fixed for the primary tuned/untuned contrast.
- Independent classifier annotations and measured configuration outcomes; grouped splits and frozen held-out analysis.
- Bounded OpenJev training after compatibility/compute checks and paid-job authorization, with provenance and total cost reporting.
- Authorized stakeholder feedback and a reproducible paper/report, including neutral or negative findings.

**Owner checkpoint:** runnable commands, expected behavior, files to inspect, evidence, and limitations after every slice; a phase-end review before any subsequent work. See [architecture](architecture.md), [evaluation](evaluation.md), [training](training-plan.md), and [technical discovery](technical-discovery.md) for retained requirements and dated findings.

## Constraints throughout

No agent-executed paid runs. The reported OpenAI credits are not spending authorization. Review each purpose-specific estimate and cap; keep cumulative cloud/non-OpenAI cash spending strictly below $50 unless separately reviewed. An authorized no-inference preflight has confirmed authentication and catalog eligibility; live coding verification remains pending. Do not commit or push unless requested. Keep secrets, private evidence/conversations, raw datasets, and course material out of Git. Claims require real evidence; unit-test mocks are never experimental results.

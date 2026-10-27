# Jev-first development plan

Updated October 25, 2026. This roadmap supersedes the earlier fixture-first sequence and inactive course schedule. **Stop after every phase for owner testing and code review. Begin the next phase only after explicit instruction.** Within later phases, deliver small reviewable slices; phase approval does not authorize unestimated spending.

## Phase 1 — Repository cleanup and direct Jev client

Preserve deferred code in an ignored verified archive. Remove simulated CLI/routing/execution components from the active package; retain prompt/category validation and Python packaging. Keep tests local and ignored. Show current and planned components in a GitHub-rendered README diagram.

Implement direct hosted TypeSafe Jev classification through the documented System One API. Use only the current prompt plus fixed category questions/definitions, with no context enrichment. Start with the existing three category fields, explicit provisional definitions, and pinned `jev-1.14.0`. Preview requests by default; live mode requires an explicit flag and API key. Reject oversize input unchanged, validate responses, preserve unknowns and missing usage, and report failures without automatic retries or invented predictions.

**Owner checkpoint:** inspect the code and request preview, run the local network-free tests, and review README architecture. Live inference is not validated by these checks. No accounts, calls, purchases, benchmarks, or training in this phase. Exact commands and files are in [README](../README.md#test-this-checkpoint-yourself).

## Phase 2 — Real Jev classification and accuracy

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

No automatic paid runs. The reported OpenAI credits are not spending authorization. Review each purpose-specific estimate and cap; keep cumulative cloud/non-OpenAI cash spending strictly below $50 unless separately reviewed. The previous declined Codex account/model inspection remains blocked without renewed authorization. Do not commit or push unless requested. Keep secrets, private evidence/conversations, raw datasets, and course material out of Git. Claims require real evidence; unit-test mocks are never experimental results.

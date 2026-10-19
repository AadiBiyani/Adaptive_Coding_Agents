# Development handoff

Prepared October 19, 2026 for a new agent working from a fresh clone.

## Goal

Build a terminal routing component that preserves a Codex coding workflow, classifies each newly submitted prompt with Jev or OpenJev, and selects a supported GPT model and reasoning effort before execution. Deliver a fine-tuned OpenJev classifier and controlled SWE-bench and multi-turn evaluation results showing correctness, cost, time, and corrective follow-ups across routing strategies.

## Current state

The project definition and Milestone 1 proposal are complete. The private submission package was finalized and its exact ZIP passed the course's structural checker on September 28, 2026. The owner explicitly confirmed the four student attestations and the stakeholder's authorization of the corrected agreement. Actual upload or grading has not been confirmed.

This development repository was empty when inspected on October 19. The initial work consists of documentation and repository hygiene only. No integration, dataset, run, training job, or measured performance result exists here. There is no build or application test command yet.

The owner supplied the original research proposal from the separate ChatGPT conversation on October 19. Its routing hypotheses, broader comparisons, and related-work leads are incorporated in `docs/research-notes.md`. Later Milestone 1 decisions narrow the initial implementation to per-user-prompt routing, GPT coding models, and the hosted/untuned/fine-tuned classifier comparisons. The pasted proposal provides background rather than a request to undo that scope.

## Files in play

| File | Role |
| --- | --- |
| `README.md` | Project orientation and clone/start instructions |
| `AGENTS.md` | Development guidance for future agents |
| `docs/project-brief.md` | Agreed problem, product scope, stakeholder need, and constraints |
| `docs/architecture.md` | Proposed integration and boundaries; not implemented |
| `docs/evaluation.md` | Comparison design and minimum experiment records |
| `docs/research-notes.md` | Original hypotheses, optional experiments, and scope evolution |
| `docs/development-plan.md` | Ordered implementation work and open decisions |
| `docs/context-sources.md` | Sources and limitations of the carried-forward context |
| `.gitignore` | Keeps evidence, secrets, generated artifacts, and raw run data out of Git |

The original course `brief.md`, `submission.yaml`, and stakeholder evidence are in the separate private Milestone 1 workspace. Do not copy the full course package into this public repository.

## What has been tried

Milestone 1 planning selected a dedicated terminal command instead of requiring an invisible modification to the stock Codex terminal UI. Earlier feasibility notes identified Codex app-server as a candidate for per-turn model/effort selection with session continuity. No integration spike was run, so current support must be verified before implementation.

A public web read of the owner's separate ChatGPT conversation failed with a cache miss. Browser discovery returned no available browser. The owner then pasted the relevant proposal, which has been incorporated. The private URL itself was not read; a fresh agent can continue from these documents without reopening it.

No model-training or benchmark approaches have failed experimentally: none have been attempted. Cloud fine-tuning was selected after the owner rejected dropping fine-tuning or limiting the project to local hardware.

## Current best approach

First prove that a small terminal client can preserve one coding session and apply a chosen model/effort configuration at each new user turn. Keep classifier adapters separate from the routing policy and coding harness. Establish measured fixed baselines and a bounded development dataset before fine-tuning. This isolates integration problems, makes comparisons fairer, and limits wasted credits.

## Next steps

1. Follow step 1 of `docs/development-plan.md`: inspect the installed Codex version and current official integration documentation, choose a minimal language/runtime, and record the supported session/configuration interface.
2. Build the smallest offline-verifiable terminal/session adapter using a stub decision source. Do not start with the training pipeline.
3. Define the candidate GPT configurations, task splits, logs, and pilot caps. Exact model IDs and spending limits are not yet agreed.
4. Run authorized fixed-baseline pilots, add classifier adapters, collect development outcomes, fine-tune OpenJev, and then run the frozen held-out comparison in that order.

## Key constraints

The initial evaluation is bug fixing/debugging. A new user prompt triggers routing; internal tool results do not independently trigger an automatic model switch. Correct task completion takes priority over cost/time. Fewer prompts means fewer corrective user follow-ups to finish a task, not fewer model or tool calls by definition.

The owner reported $3,000 in GPT API credits during planning and wants to use as little as possible. The current balance, expiry, API access, and separate cash compute budget have not been verified. No particular cloud provider, GPU, exact task count, model ID, numerical reliability tolerance, language, or training recipe is locked in.

Hosted TypeSafe Jev and independent OpenJev are distinct. Fine-tuning OpenJev remains a desired deliverable. SWE-bench results remain a central output. Published leaderboard numbers are context rather than a controlled baseline. Keep the handoff committed because the owner explicitly requested context that survives cloning; no local memory service should be required to understand the repository.

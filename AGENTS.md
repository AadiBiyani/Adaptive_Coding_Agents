# Development instructions

This is the development repository for Adaptive Model and Reasoning Selection for AI Coding Agents. The separate course submission package has its own evidence and packaging rules; do not import that package's submission-only workflow into product development.

## Read before continuing

Read `HANDOFF.md`, then `docs/project-brief.md`, `docs/architecture.md`, `docs/evaluation.md`, and `docs/development-plan.md`. `docs/research-notes.md` preserves broader ideas from the original proposal; its optional experiments do not expand the initial scope automatically. The latest user instruction takes precedence over these planning documents. Distinguish confirmed decisions, proposed implementation details, and measured results. Update the handoff when the actual state changes.

## Preserve the agreed scope

- Build a dedicated terminal command that preserves the Codex coding workflow and session context.
- Route before each newly submitted user prompt using that prompt and bounded information already available at that point. Mid-turn routing is outside the initial scope.
- Select both a supported GPT model and reasoning effort from an explicit configuration registry. Do not assume every model supports the same effort values.
- Begin with bug fixing and debugging. Keep SWE-bench evaluation, a small controlled multi-turn evaluation, and qualitative stakeholder feedback in the plan.
- Compare hosted TypeSafe Jev, untuned OpenJev, and fine-tuned OpenJev, alongside strong fixed and simple-rule baselines. Do not describe OpenJev as the hosted model's released weights or claim equivalence without evidence.
- Prioritize correctness, then cost and time among similarly reliable choices. Desired improvements are hypotheses until measured.

## Work and verification

Verify current Codex interfaces, model availability, supported settings, and training requirements against installed versions and official documentation before depending on them. The architecture document describes a candidate integration, not an existing working hook or API contract.

Implement small reviewable slices. Use meaningful checks for behavior that matters: session continuity, actual configuration selection, fallback handling, budgets, accounting, and reproducible evaluation. Keep offline checks runnable without API credentials. Do not run benchmark code from unknown repositories directly on the developer's host; use the benchmark's isolated evaluation workflow.

Do not report a task as solved because the router or coding model says it is solved. Executable evaluation determines correctness. Keep hidden evaluation checks and future outcomes out of router inputs, and never train or select policies on held-out results. Commit reproducibility metadata with reported results.

## Resources and records

The owner wants to minimize API usage. Available credits are not a spending target or authorization for unlimited calls. Exact API spending limits and a separate cloud-training/hosting/benchmark-compute cap remain undecided. Define caps and obtain the owner's authorization before paid experiments; once authorized, work within those caps without repeatedly seeking permission for each routine call. Do not provision cloud GPUs or start training during documentation setup.

Track classifier calls, coding calls, retries, failed attempts, tokens, cost, latency, and configuration changes. Distinguish actual billed usage from estimates and track training/hosting/benchmark compute separately from inference.

## Public repository hygiene

Keep stakeholder evidence, personal contact details, student identifiers, course submissions, secrets, raw private conversations, private repositories, and unreleased organizational material out of Git. Do not assume access to the stakeholder's former employer's code or benchmark. `.gitignore` is a guardrail; inspect staged files before committing. Use environment variables or ignored local configuration for credentials when runtime code is added.

Do not fabricate approval, participant feedback, benchmark results, fine-tuning outcomes, or course completion. The committed `docs/project-brief.md` is a development summary; the original approved brief and evidence remain in the private Milestone 1 package.

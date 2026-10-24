# Development instructions

This is the development repository for Adaptive Model and Reasoning Selection for AI Coding Agents. The separate course submission package has its own evidence and packaging rules; do not import that package's submission-only workflow into product development.

## Read before continuing

Read `HANDOFF.md`, then `docs/project-brief.md`, `docs/architecture.md`, `docs/evaluation.md`, and `docs/development-plan.md`. `docs/research-notes.md` preserves broader ideas from the original proposal; its optional experiments do not expand the initial scope automatically. The latest user instruction takes precedence over these planning documents. Distinguish confirmed decisions, proposed implementation details, and measured results. Update the handoff when the actual state changes.

The owner deleted the premature prototype and set the Milestone 2 schedule aside. `docs/development-plan.md` is the primary roadmap; the milestone plan is an inactive course reference. Phase 0 requirements/discovery is complete. The owner subsequently delegated conservative defaults and said coding would begin tomorrow: `docs/first-build-defaults.md` now specifies the first offline slice for the next resumed development session. Broader research/live-adapter decisions remain gated in `docs/phase-1-specification.md`. Read `docs/research-review.md` for dated findings and `docs/training-plan.md` before OpenJev adaptation. Do not restore deleted prototype code.

## Preserve the agreed scope

- Build a dedicated terminal command that preserves the Codex coding workflow and session context.
- The owner has no TypeScript requirement; that came from an earlier agent recommendation. Python-first is the selected design direction to reduce policy/data duplication. Pin a compatible client distribution and validate its live behavior in the planned stages. Share one coding execution path between product and benchmarks and do not add a second client merely to use both languages.
- Route before each newly submitted user prompt. Jev/OpenJev receives only that specific prompt as dynamic task content, plus fixed category questions/definitions. Do not append history, summaries, repository metadata/content, tool results, or prior failures. Codex retains its coding-session context. Mid-turn routing is outside the initial scope.
- Jev/OpenJev classifies the prompt into a task type plus a few signals; a separate policy maps those labels to a model/effort configuration. This supersedes the earlier direct-configuration-choice proposal. Refine categories on training/development examples and version them; see `docs/phase-1-specification.md`.
- The owner selected automatic reliable fallback for prompts too vague to classify, within remaining budget and availability. Exact fallback settings remain to be selected from development evidence. Preserve unknowns; do not add context or interrupt for router-only clarification. Training annotations and matched classifier/rule controls use the same prompt-only information boundary.
- Select both a supported GPT model and reasoning effort from an explicit configuration registry. Do not assume every model supports the same effort values.
- Begin with bug fixing and debugging. Keep SWE-bench evaluation, a small controlled multi-turn evaluation, and qualitative stakeholder feedback in the plan.
- The owner selected Python repositories for the initial training/benchmark cohort. Distinguish task language from implementation language; broader coverage is a later decision.
- Compare hosted TypeSafe Jev, untuned OpenJev, and fine-tuned OpenJev, alongside strong fixed and simple-rule baselines. Do not describe OpenJev as the hosted model's released weights or claim equivalence without evidence.
- The first study's primary question is whether fine-tuning OpenJev improves routing over untuned OpenJev, producing better task performance or lower cost/token usage. Keep the matched tuned/untuned contrast central; multi-turn adaptation is a secondary analysis.
- For that primary contrast, hold the category definitions and downstream routing policy fixed. Separate decision-time category annotations for classifier training from executable configuration outcomes used to establish the routing policy.
- Include a cheap learned control for the paper study. Require claim-specific ablations before attributing gains to joint selection or adaptation across user messages; a standard one-prompt SWE-bench run cannot establish the latter.
- Prioritize correctness, then cost and time among similarly reliable choices. Desired improvements are hypotheses until measured.
- The first version is for research and personal testing, as confirmed during Phase 0. Do not treat that scope as permission for commercial model deployment or access to employer material.

## Work and verification

Verify current Codex interfaces, model availability, supported settings, and training requirements against installed versions and official documentation before depending on them. The architecture document describes a candidate integration, not an existing working hook or API contract.

Settle each slice's requirements, contracts, dependencies, cost boundary, and acceptance checks before implementation. The owner selected the conservative offline defaults for development on the next resumed session; do not treat this as authorization for live calls, benchmark execution, or training. Implement small reviewable slices. Use meaningful checks for behavior that matters: session continuity, actual configuration selection, fallback handling, budgets, accounting, and reproducible evaluation. Keep offline checks runnable without API credentials. Do not run benchmark code from unknown repositories directly on the developer's host; use the benchmark's isolated evaluation workflow.

Do not report a task as solved because the router or coding model says it is solved. Executable evaluation determines correctness. Keep hidden evaluation checks and future outcomes out of router inputs, and never train or select policies on held-out results. Commit reproducibility metadata with reported results.

## Resources and records

The owner reports $3,333 in OpenAI API credits and wants minimal use for necessary validation, class submissions, and ML-paper experiments. Balance, eligibility, and expiry are unverified. Use offline checks and included development tooling where suitable. Available credits are not a spending target or authorization for calls. Cloud spending must remain strictly under $50 cumulatively; conservatively plan other non-OpenAI cash costs inside that ceiling until separately reviewed. Linux-server access and any included cloud credits are unverified. The owner will choose the API cap after a run-by-run estimate, not a preset allowance. Define purpose-specific stage caps and obtain the owner's authorization before paid experiments; once authorized, work within those caps without repeatedly seeking permission for each routine call. Do not provision cloud GPUs or start training during documentation setup.

The previous live account/model inspection escalation was declined. Do not retry it or bypass that restriction without renewed authorization. Read-only documentation and offline design can continue.

Track classifier calls, coding calls, retries, failed attempts, tokens, cost, latency, and configuration changes. Distinguish actual billed usage from estimates and track training/hosting/benchmark compute separately from inference.

For research, keep competitive controls, grouped splits, paired uncertainty, and a predeclared reliability criterion. Count collection and checkpoint-selection costs. Never claim novelty, equivalence, or a universally best model from a pilot; tune only on training/development data and freeze before held-out evaluation.

## Public repository hygiene

Keep stakeholder evidence, personal contact details, student identifiers, course submissions, secrets, raw private conversations, private repositories, and unreleased organizational material out of Git. Do not assume access to the stakeholder's former employer's code or benchmark. `.gitignore` is a guardrail; inspect staged files before committing. Use environment variables or ignored local configuration for credentials when runtime code is added.

Do not fabricate approval, participant feedback, benchmark results, fine-tuning outcomes, or course completion. The committed `docs/project-brief.md` is a development summary; the original approved brief and evidence remain in the private Milestone 1 package.

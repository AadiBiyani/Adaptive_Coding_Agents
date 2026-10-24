# Development plan

## Primary goal

A developer can finish debugging tasks in a continuous Codex terminal session while Jev/OpenJev classifies each new user prompt into a task type plus signals and a separate routing policy chooses the GPT model and reasoning effort. Deliver the router, a cloud-fine-tuned OpenJev classifier, and reproducible executable evidence of when routing helps, hurts, or makes no meaningful difference to correctness, cost, and time.

Updated October 24, 2026. This is the primary roadmap. The owner set the Milestone 2 schedule aside and requested deletion of the premature prototype; the prototype, its archive, and generated schemas have been deleted. The repository contains planning documents only. No implementation phase is complete and no model, training, or benchmark result is claimed.

## How we will work

Resolve each slice's requirements and review its design before code. Phases 0 and 1 establish those contracts. The owner has now delegated conservative defaults and scheduled the first independent offline slice for the next resumed development session; [First-build defaults](first-build-defaults.md) defines it. Broader research/live-adapter decisions remain gates before their dependent work. Each slice needs clear inputs, outputs, checks, costs, and dependencies. A recommendation is not evidence of live integration; experimental unknowns must not be silently marked resolved.

The owner has no fixed language preference. Python is the selected design direction for the initial client/router and research tooling, reducing cross-language policy/data duplication. Verify compatible published pins for the source-inspected app-server client; retain TypeScript as a fallback for a demonstrated need. Keep one coding execution path for interactive use and benchmarks. [Architecture](architecture.md), [Evaluation](evaluation.md), and [Training plan](training-plan.md) specify responsibilities; [Research review](research-review.md) explains candidates and related work. [Phase 0 decisions](phase-0-decisions.md) records the completed requirements/discovery review.

No paid experiment has been started or authorized for execution during planning. The owner reports $3,333 in OpenAI API credits and wants to preserve them for necessary validation, submissions, and paper experiments. Routine development should use offline checks and included tooling where suitable. Cloud spending must remain strictly under $50 cumulatively; conservatively plan other non-OpenAI cash costs inside that ceiling until reviewed. The owner will choose the API cap after a run-by-run estimate, rather than accepting a preset $10 or $25 allowance. Before each paid stage, define its purpose, runs, limits, stop condition, and retained artifact; work within the resulting authorization without repeated per-call requests.

## Requirements that must stay coherent

| Requirement | Acceptance evidence when implemented |
| --- | --- |
| Preserve the Codex workflow | Repository, tools, approvals, follow-ups, cancellation, and session resumption work through the pinned harness. |
| Route at new user prompts | One decision before each new user turn; internal model/tool steps do not trigger rerouting. |
| Classify before selecting a configuration | Jev/OpenJev emits versioned task categories/signals; a separate policy chooses model/effort from those labels and measured performance. |
| Select model and effort | Choices come from a supported registry; requested, accepted, and observable executed settings are distinguished. |
| Prioritize correctness | External executable checks determine success; cheaper choices follow a predefined reliability policy. |
| Compare the required classifiers | Hosted Jev, released OpenJev, and the same OpenJev checkpoint after project fine-tuning use comparable permitted information and GPT choices. |
| Produce credible benchmark evidence | SWE-bench initial-routing results, a separate multi-turn study, competitive controls, uncertainty, and reproducibility metadata. |
| Account for resources | Include failures, retries, classifier and switching overhead; separate inference, label collection, training, hosting, and benchmark compute. |
| Support a defensible paper | Claims match controlled evidence and related work; negative results remain valid outcomes. |

## Phase 0 — Documentation discovery and design decisions

**How this serves the primary goal:** Establish an implementable design and a defensible research question before creating another prototype.

1. Review [Technical discovery](technical-discovery.md) and [Research review](research-review.md). Version-matched Codex schemas were inspected; live execution was not verified. Do not retry the previously declined account-inspection escalation without renewed authorization.
2. Choose the language/runtime from actual interface coverage and maintenance needs. Compare Python-first with a thin TypeScript client plus Python research tooling; neither is an owner-imposed requirement. Candidate tooling is Python 3.12/uv and, only if needed, Node.js 24 LTS/npm. Separate GPU dependencies from the evaluator.
3. Review the app-server stdio contract: initialization, thread start/resume, explicit per-turn model/effort, approvals, cancellation, and usage. Queue new prompts while a turn is active. Record what execution and billing detail the interface cannot prove.
4. Identify OpenJev precisely as `openjev/openjev`, an independent 27B checkpoint. Review its license, pinned helper/readout, adapter compatibility, and memory risks using the training plan. Serving instructions do not establish a tested training recipe.
5. Narrow the paper claim against the closest routing work. A candidate is live executable evidence about classifier adaptation and joint selection at developer-message boundaries, including the cost of obtaining that adaptation.
6. Review dataset candidates, isolated evaluation architecture, and billing paths. Codex subscription access, direct OpenAI API credits, hosted Jev, and GPU/benchmark compute are separate resources.

**Output / done:** Phase 0's requirements/discovery review is complete; [Phase 0 decisions](phase-0-decisions.md) records the owner's answers, selected design direction, inspected source interfaces/readout, and later validation gates. This is not proof of live integration or training feasibility. Phase 1's exact contracts must be settled before coding.

**References:** [Architecture](architecture.md), [Training plan](training-plan.md), and primary sources in [Research review](research-review.md).

**Guards:** Do not infer a stock-terminal hook, training fit, commercial permission, model access, or novelty from a plausible design. Do not substitute a different similarly named OpenJev model to conceal a feasibility problem.

## Phase 1 — Specify the first implementation and experiment

**How this serves the primary goal:** Give components precise contracts and ensure that initial paid measurements can be reused in the research.

**Current state:** The first offline implementation contract is selected in [First-build defaults](first-build-defaults.md), following the owner's request for conservative defaults and coding tomorrow. [Phase 1 specification](phase-1-specification.md) retains the confirmed product flow and later research/live gates. Research labels, compatible real-adapter pins, and experiment details are not declared complete. No code has been written tonight.

1. Specify terminal start/resume, prompt queueing, visible routing decisions, streaming, approvals, cancellation, and errors. Review the state transitions before writing the client.
2. Define versioned taxonomy, configuration, routing-state, classification, policy-decision, usage, and run records. Enforce current-prompt-only classifier inputs; fix maximum size/oversized-input handling and unknown-usage semantics. Codex keeps its execution context. Share JSON Schema contracts between the terminal, runner, and persisted artifacts.
3. Jev/OpenJev predicts task categories/signals; a separate policy maps them to an eligible model/effort configuration using measured performance. Refine category definitions and annotation rules on development examples. Define shared mapping construction, sparse/unknown-category behavior, fallback, timeouts, retries, pending-usage reservation, and stop behavior. Category confidence is not task-success probability.
4. Review a two-model/two-effort candidate pool: `gpt-6-luna` and `gpt-6.1-sol`, each at `low` and `high`, contingent on access. Specify tier, context/output limits, and version logging. These are candidates, not measured winners.
5. Define development tasks, selection rules, train/development/held-out groups, permitted inputs, visible tests, private checks, and limits. Select a final SWE-bench cohort/version after environment feasibility is known, before label collection.
6. Write the multi-turn protocol: required new requirements versus corrective follow-ups, permitted visible feedback, completion rules, and scenario limits. Every strategy faces the same information policy.
7. Separate decision-time category annotations from measured configuration outcomes. Define category ambiguity/unknowns, correctness-first policy evidence, all-failure cases, the fixed-policy tuned/untuned contrast, and reliability criteria. Set the numerical reliability margin and final sample plan from stakeholder needs and development evidence before held-out evaluation.
8. Set resource caps for the next paid stage only. Confirm credit eligibility/expiry privately. Reserve final-evaluation funding before extensive label collection or training; the entire balance is not an experiment budget.

**Output / done:** Each implementation slice has reviewed contracts that require no guessed behavior. The independent offline foundation now meets that specification criterion and is the owner's next-session starting point. Live integration and experiment implementation additionally require their remaining contracts/pins, and paid work requires an explicit cap. The full Phase 1 research specification is not marked complete.

**References:** [Classifier contract](architecture.md#classifier-and-policy-contract), [Minimum records](evaluation.md#minimum-records-to-implement), [Training labels](training-plan.md#outcome-data-and-labels).

**Guards:** Do not implement unresolved behavior or enable real providers through a fixture path. Do not require final-study conclusions before the reviewed offline foundation or pilot, or use uncertainty to justify an uncontrolled experiment. No coding tonight; the owner plans to resume tomorrow.

## Phase 2 — Prove the shared terminal and execution foundation

**How this serves the primary goal:** Verify session continuity, configuration control, and accounting before classifier or training experiments.

1. Once the design is clear and coding is requested, create the minimal package in the Phase 0-selected Python stack. Follow the pinned app-server initialization/thread/turn contract through the verified client interface. Start with fixed/stub decisions.
2. Implement the reviewed terminal state transitions and the same callable execution path for benchmarks. Preserve Codex tool execution and approval boundaries.
3. Add registry validation, the confirmed automatic fallback behavior, prompt-size limits, usage records, and budget checks. Verify that history/repository/tool details do not enter classifier inputs. Reserve for in-flight work; stop new calls at limits and reconcile eventual usage.
4. Check continuity, resume, settings, interleaved events, cancellation, invalid routes, missing usage, retries, and exhausted budgets using offline fixtures.
5. Run the smallest authorized live check that proves two turns, a model/effort change, and resumption. If the integration cannot honor required settings or preserve the workflow, revise the architecture before expanding it.

**Output / done:** A reproducible session trace proves supported behavior. Fields described as observed have an event/provider record; unknowns remain explicit. Offline checks need no credentials.

**References:** [Codex integration](architecture.md#codex-integration), [Documented interfaces](technical-discovery.md#documented-codex-interface-candidates), official app-server sections “Getting started,” “Start a turn,” and “Approvals.”

**Guards:** Do not build a second agent harness, confuse `turn/steer` with configurable new turns, or claim itemized costs from aggregate usage.

## Phase 3 — Build the evaluator and measure the routing opportunity

**How this serves the primary goal:** Establish trustworthy outcomes and discover whether configuration differences justify learned routing.

1. Build the Python runner around the shared Codex execution path. Pin tasks, repository commits, evaluator revision, images, architecture, limits, and artifact identifiers.
2. Run coding tools and evaluator code in the designated isolated environment. Validate patch application, known success/failure fixtures, clean regrading, and failure categories before buying model runs.
3. Run a small authorized fixed-configuration pilot on development tasks. Reuse valid records; repeat when variability or changed conditions warrants it.
4. Select strong fixed controls on development data. Examine the cost–success frontier and an explicitly retrospective oracle upper bound to diagnose headroom; the oracle is not deployable.
5. Use per-task cost and variance to size later collection/evaluation. Inspect whether prompt-only categories provide useful signal and whether unknowns/fallbacks dominate. Review a separately scoped context experiment before large paid expansion if missing information appears limiting. Validate the multi-turn environment and stopping policy independently of the classifier.

**Output / done:** Each pilot result has a patch, executable outcome, manifest, and usage record. Recommend proceeding, narrowing the claim, adjusting the pool using development evidence, or pausing paid expansion for lack of routing opportunity.

**References:** [SWE-bench output](evaluation.md#swe-bench-output), [Multi-turn tasks](evaluation.md#multi-turn-tasks), [official evaluator guide](https://www.swebench.com/SWE-bench/guides/evaluation/).

**Guards:** No leaderboard substitution, host execution of untrusted benchmark code, favorable-task selection, or strong reliability claims from a tiny pilot. A negative pilot does not silently cancel fine-tuning; review the feasibility/cost trade-off with the owner.

## Phase 4 — Add classifier adapters and competitive controls

**How this serves the primary goal:** Isolate Jev's routing value before attributing improvement to project fine-tuning.

1. Implement transparent deterministic rules. Prepare the shared category-to-configuration policy and a cheap learned category classifier using the same permitted state/annotations, such as TF-IDF plus regularized linear classifiers; paid embeddings are unnecessary initially.
2. Add hosted Jev and released OpenJev behind the typed category/signal contract. Follow pinned examples linked in discovery/training and validate serialization, per-question scoring/accounting, failures, and provenance.
3. Batch authorized development comparisons through the same harness, GPT pool, budgets, information policy, and evaluator. Batch OpenJev work to avoid idle hosting charges.
4. Establish a shared taxonomy, mapping, precision, templates, and calibration settings for the later untuned/tuned comparison. Refine the mapping with Phase 5 evidence before freezing it for final checkpoint comparison/selection. Record limitations on hosted-version control.

**Output / done:** Fixed, rules, hosted Jev, and untuned OpenJev have comparable execution paths; the cheap learned control is ready for Phase 5 labels. Classifier and switching overhead are included in totals.

**References:** [Strategies](evaluation.md#strategies), [Classifier dependencies](technical-discovery.md#classifier-dependencies), [Training plan](training-plan.md).

**Guards:** Do not change coding context when changing the router or substitute a rules demo for the classifier comparison.

## Phase 5 — Construct category labels and routing-performance data

**How this serves the primary goal:** Train a task classifier on reviewed categories and establish the downstream policy from executable configuration outcomes.

1. Annotate task types and signals using the reviewed taxonomy and current prompt only. Share those examples across the cheap learned classifier and OpenJev; record annotation quality, ambiguity, and unknowns. Extra execution-state metadata is excluded from the annotation view and classifier features.
2. Separately measure candidate configuration outcomes on predefined training states under a capped, development-informed sampling plan. Use the reviewed reliability rule to inform the common category-to-configuration mapping. Preserve ties, uncertainty, failed candidates, and all-failure states rather than forcing a successful winner.
3. Start with reproducible initial states. Later-turn configuration comparisons require the same valid Codex conversation and repository state for each candidate; annotations use only the current user prompt. Disclose initial-only training/policy evidence if comparable later-state replay is infeasible.
4. Audit duplicates, related issues, split isolation, leakage, annotation/option imbalance, and provenance. Freeze taxonomy, dataset, annotation-rule, and mapping versions at their specified gates.

**Output / done:** Category examples trace to decision-time inputs and reviewed annotations; policy evidence traces to measured coding outcomes. Held-out tasks have not influenced categories, labels, prompts, configurations, or policies.

**References:** [Training data and leakage](evaluation.md#training-data-and-leakage-controls), [Outcome data and labels](training-plan.md#outcome-data-and-labels).

**Guards:** Different later trajectories are not interchangeable counterfactual states. A single lucky run is not proof of a generally superior route; repeat important ambiguous cases only within the cap.

## Phase 6 — Fine-tune OpenJev with bounded cloud compute

**How this serves the primary goal:** Deliver the requested specialized model and test whether adaptation repays its costs.

1. Use the inspected checkpoint/helper contract and select a supported adapter setup, rechecking source changes if revisions differ. Supervised option-token LoRA is the proposed first method; QLoRA depends on architecture/backward-pass compatibility. No reinforcement-learning loop is planned initially.
2. Compare current offers by expected completed-job cost, including setup, downloads, storage, evaluation, and shutdown. Verify availability before naming the cheapest suitable GPU.
3. Run one capped compatibility job: finite loss/gradients, frozen base and changing adapters, peak memory/step time, checkpoint save/reload, and valid option scores. Stop on failure; do not escalate hardware automatically.
4. Train a small predeclared candidate set within the cap using category-option supervision. Select checkpoints on development data under the frozen shared mapping and report the selection budget. Match untuned/tuned inference/calibration conditions; separately refitting calibration or mapping is a distinct comparison.
5. Compare coding outcomes as well as classification fit. Record checkpoint/tokenizer hashes, labels, hyperparameters, seeds, hardware, runtime, and total cost.

**Output / done:** A retrievable adapted checkpoint passes serving checks and has a controlled development comparison. Completing training does not establish better routing.

**References:** [Training plan](training-plan.md), including its compatibility gate and primary Transformers/PEFT references.

**Guards:** Do not infer training fit from an inference recipe, default to a large search, or silently replace the OpenJev checkpoint.

## Phase 7 — Freeze and evaluate the paper claims

**How this serves the primary goal:** Measure generalization under a protocol that cannot be adjusted to favor the router after final results are seen.

1. Freeze manifests, code, harness, GPT configurations, taxonomy/questions, classifier checkpoints, shared mapping, policies, budgets, repetitions, failure handling, reliability margin, and analysis before held-out runs.
2. Evaluate the required strategies and cheap learned control on paired tasks. Balance execution order, isolate state, distinguish run IDs, and log service versions. Execute dynamic policies live.
3. Include initial-only versus per-user-turn selection for an adaptation-benefit claim. Include model-only and effort-only controls for a claim that joint selection beats either alone. Avoid an automatic full cross-product.
4. Report success first, paired uncertainty, full attempt cost, cost per resolved task, latency, regressions, and corrective follow-ups. Include failures, timeouts, and exhausted budgets; apply the frozen infrastructure-failure rule.
5. Include collection/training/hosting costs and possible amortization. If the affordable sample cannot support the desired reliability statement, report an exploratory result instead of equivalence.

**Output / done:** Results and executable artifacts support each retained claim, including neutral or negative findings.

**References:** [Reporting and success criteria](evaluation.md#reporting-and-success-criteria), [Research review](research-review.md).

**Guards:** No favorable-step stitching, held-out checkpoint selection, correlated-turn pseudo-replication, or interpreting “not significant” as “equally reliable.”

## Phase 8 — Verify delivery and prepare reproducible research

**How this serves the primary goal:** Make the workflow usable by the stakeholder and its claims inspectable by another researcher.

1. Verify a fresh checkout can install supported versions, pass offline checks, use the terminal, retrieve permitted artifacts, and reproduce a small authorized evaluation.
2. Check implementations against pinned documentation, including settings, failure accounting, split isolation, and training behavior; resolve material discrepancies.
3. Conduct a bounded stakeholder trial and obtain authorized qualitative feedback. Keep private evidence outside Git; scripted prompt savings are not measured human productivity.
4. Write methods, related work, results, uncertainty, limitations, artifact/license notes, and a claim-to-evidence table. Assess venue fit and current requirements when the study is mature enough.
5. Update README and handoff with actual capabilities and reproducibility instructions. Course packaging can be handled separately when requested.

**Output / done:** Deliver the router, tuned classifier/provenance, benchmark report, and workflow feedback. A paper is an intended output, not a promised acceptance or positive result.

**References:** [Project brief](project-brief.md), [Repository instructions](../AGENTS.md), [Context/privacy boundaries](context-sources.md).

**Guards:** Do not publish private stakeholder traces, unlicensed artifacts, invented feedback, or unsupported novelty claims.

## Decision ledger and next review

| Decision | Current status | Resolution needed |
| --- | --- | --- |
| Product/domain/boundary | Confirmed: terminal, debugging, new user prompts, GPT model plus effort | Preserve throughout design. |
| Languages | Python-first selected on technical merit; owner has no TypeScript requirement | Verify compatible published pins for the source-inspected client before setup. |
| Intended use | Confirmed: research and personal testing first | Respect checkpoint terms; commercial deployment is a later decision. |
| Integration | Recommended: pinned app-server stdio, one execution path | Finish state/approval/usage contract; later bounded live proof. |
| Classifier and policy outputs | Confirmed: task type plus signals, then separate model/effort selection | Refine taxonomy/annotations, shared mapping, and timeout/retry rules; see Phase 1 specification. |
| Classifier input and ambiguity | Confirmed: current prompt only; automatic reliable fallback | Specify prompt-size/oversized handling and select fallback settings from development evidence; Codex retains session context. |
| GPT pool | Proposed: two models × low/high | Verify access/execution and measure quality before naming winners. |
| OpenJev identity | `openjev/openjev` 27B; pinned helper inspected and hash verified; research use selected | Validate tokenizer, training loss, adapter behavior, and GPU fit in their planned stages. |
| Training | Proposed supervised LoRA; QLoRA conditional | Verify backward pass/memory in a capped job before full training. |
| Benchmark | Python repositories first confirmed; SWE-bench plus multi-turn study retained | Select cohort/version, container path, splits, and follow-up rules. |
| Reliability/statistics | Correctness first and tuned/untuned primary contrast confirmed | Choose numeric margin, ambiguity policy, exact analysis, and affordable precision before final evaluation. |
| Funding | $3,333 API credits reported; under-$50 cumulative cloud ceiling; estimate-first API approval | Verify access/credits privately and review exact batches before paid work. |
| Paper | Owner chose fine-tuned versus untuned OpenJev as the primary research contrast | Measure executable success, cost, and tokens; retain fixed/rules/learned/hosted controls and secondary multi-turn analysis. |

**Immediate next step:** At the next resumed development session, prepare the isolated Python 3.12 environment and implement the offline records, validation, fixture routing/fallback, accounting, and simulated session path in [First-build defaults](first-build-defaults.md). Finish the remaining [Phase 1](phase-1-specification.md) research/live-adapter gates before those features. Phase 0 live validation gates remain scheduled, not passed. Extra classifier context, mid-turn routing, broad feature tasks, and a public gateway remain outside the initial slice.

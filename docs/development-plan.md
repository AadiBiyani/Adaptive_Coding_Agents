# Development plan

## Primary goal

A developer can finish debugging tasks in a continuous Codex terminal session while a router chooses a GPT model and reasoning effort before each new user prompt. Deliver the router, a cloud-fine-tuned OpenJev classifier, and reproducible executable evidence of when routing helps, hurts, or makes no meaningful difference to correctness, cost, and time.

Updated October 24, 2026. This is the primary roadmap. The owner set the Milestone 2 schedule aside and requested deletion of the premature prototype; the prototype, its archive, and generated schemas have been deleted. The repository contains planning documents only. No implementation phase is complete and no model, training, or benchmark result is claimed.

## How we will work

Resolve requirements and review the design before writing code. Phases 0 and 1 are planning. Each later phase needs clear inputs, outputs, references, acceptance checks, cost boundaries, and dependencies before implementation starts. A recommendation is not evidence that a live integration works. Questions requiring experiments belong in explicitly bounded validation steps; they must not be silently marked resolved.

Use TypeScript for the terminal/router/Codex client and Python for data, training, benchmark orchestration, and analysis. Keep one coding execution path for interactive use and benchmarks. [Architecture](architecture.md), [Evaluation](evaluation.md), and [Training plan](training-plan.md) specify those responsibilities; [Research review](research-review.md) explains the technology choices and related work.

No paid work is currently authorized. The owner reports $3,333 in OpenAI API credits and wants to preserve them for necessary validation, submissions, and paper experiments. Routine development should use offline checks and included development tooling where suitable. Exact API and separate cash-compute caps remain open. Before each paid stage, agree a batch purpose, maximum resource use, stop condition, and retained artifact; then execute within that authorization without repeated per-call permission requests.

## Requirements that must stay coherent

| Requirement | Acceptance evidence when implemented |
| --- | --- |
| Preserve the Codex workflow | Repository, tools, approvals, follow-ups, cancellation, and session resumption work through the pinned harness. |
| Route at new user prompts | One decision before each new user turn; internal model/tool steps do not trigger rerouting. |
| Select model and effort | Choices come from a supported registry; requested, accepted, and observable executed settings are distinguished. |
| Prioritize correctness | External executable checks determine success; cheaper choices follow a predefined reliability policy. |
| Compare the required classifiers | Hosted Jev, released OpenJev, and the same OpenJev checkpoint after project fine-tuning use comparable permitted information and GPT choices. |
| Produce credible benchmark evidence | SWE-bench initial-routing results, a separate multi-turn study, competitive controls, uncertainty, and reproducibility metadata. |
| Account for resources | Include failures, retries, classifier and switching overhead; separate inference, label collection, training, hosting, and benchmark compute. |
| Support a defensible paper | Claims match controlled evidence and related work; negative results remain valid outcomes. |

## Phase 0 — Documentation discovery and design decisions

**How this serves the primary goal:** Establish an implementable design and a defensible research question before creating another prototype.

1. Review [Technical discovery](technical-discovery.md) and [Research review](research-review.md). Version-matched Codex schemas were inspected; live execution was not verified. Do not retry the previously declined account-inspection escalation without renewed authorization.
2. Adopt the TypeScript/Python division. Recommended tooling is Node.js 24 LTS with npm and candidate Python 3.12 environments managed with uv. Resolve exact compatible pins before installation; separate GPU dependencies from the evaluator.
3. Review the app-server stdio contract: initialization, thread start/resume, explicit per-turn model/effort, approvals, cancellation, and usage. Queue new prompts while a turn is active. Record what execution and billing detail the interface cannot prove.
4. Identify OpenJev precisely as `openjev/openjev`, an independent 27B checkpoint. Review its license, pinned helper/readout, adapter compatibility, and memory risks using the training plan. Serving instructions do not establish a tested training recipe.
5. Narrow the paper claim against the closest routing work. A candidate is live executable evidence about classifier adaptation and joint selection at developer-message boundaries, including the cost of obtaining that adaptation.
6. Review dataset candidates, isolated evaluation architecture, and billing paths. Codex subscription access, direct OpenAI API credits, hosted Jev, and GPU/benchmark compute are separate resources.

**Output / done:** The decision ledger distinguishes adopted requirements, recommendations, and unknowns. Blocking design ambiguities have a chosen resolution; empirical feasibility checks have an explicit later test and failure response. Phase 0 remains open.

**References:** [Architecture](architecture.md), [Training plan](training-plan.md), and primary sources in [Research review](research-review.md).

**Guards:** Do not infer a stock-terminal hook, training fit, commercial permission, model access, or novelty from a plausible design. Do not substitute a different similarly named OpenJev model to conceal a feasibility problem.

## Phase 1 — Specify the first implementation and experiment

**How this serves the primary goal:** Give components precise contracts and ensure that initial paid measurements can be reused in the research.

1. Specify terminal start/resume, prompt queueing, visible routing decisions, streaming, approvals, cancellation, and errors. Review the state transitions before writing the client.
2. Define versioned configuration, routing-state, decision, usage, and run records. Fix context selection/truncation and unknown-usage semantics. Share a JSON Schema boundary between TypeScript and Python.
3. Start with a typed choice among eligible configuration IDs, then deterministic validation and fallback. Choose fallback, timeouts, retries, pending-usage reservation, and stop behavior explicitly. Confidence is not a success probability.
4. Review a two-model/two-effort candidate pool: `gpt-6-luna` and `gpt-6.1-sol`, each at `low` and `high`, contingent on access. Specify tier, context/output limits, and version logging. These are candidates, not measured winners.
5. Define development tasks, selection rules, train/development/held-out groups, permitted inputs, visible tests, private checks, and limits. Select a final SWE-bench cohort/version after environment feasibility is known, before label collection.
6. Write the multi-turn protocol: required new requirements versus corrective follow-ups, permitted visible feedback, completion rules, and scenario limits. Every strategy faces the same information policy.
7. Define correctness-first labels, ambiguous/all-failure cases, primary comparisons, and reliability criteria. Set the numerical reliability margin and final sample plan from stakeholder needs and development evidence before held-out evaluation.
8. Set resource caps for the next paid stage only. Confirm credit eligibility/expiry privately. Reserve final-evaluation funding before extensive label collection or training; the entire balance is not an experiment budget.

**Output / done:** Reviewed contracts and an experiment specification contain no unresolved behavior that the first implementation would have to guess. The owner is ready to proceed to coding; paid work additionally has an explicit cap. Writing this roadmap does not establish these conditions.

**References:** [Classifier contract](architecture.md#classifier-and-policy-contract), [Minimum records](evaluation.md#minimum-records-to-implement), [Training labels](training-plan.md#outcome-data-and-labels).

**Guards:** No scaffolding while requirements are being settled. Do not require final-study conclusions before a pilot, or use that uncertainty to justify an uncontrolled pilot.

## Phase 2 — Prove the shared terminal and execution foundation

**How this serves the primary goal:** Verify session continuity, configuration control, and accounting before classifier or training experiments.

1. Once the design is clear and coding is requested, create the minimal TypeScript package. Follow the pinned app-server initialization/thread/turn examples and generate matching protocol types. Start with fixed/stub decisions.
2. Implement the reviewed terminal state transitions and the same callable execution path for benchmarks. Preserve Codex tool execution and approval boundaries.
3. Add registry validation, fallback, context limits, usage records, and budget checks. Reserve for in-flight work; stop new calls at limits and reconcile eventual usage.
4. Check continuity, resume, settings, interleaved events, cancellation, invalid routes, missing usage, retries, and exhausted budgets using offline fixtures.
5. Run the smallest authorized live check that proves two turns, a model/effort change, and resumption. If the integration cannot honor required settings or preserve the workflow, revise the architecture before expanding it.

**Output / done:** A reproducible session trace proves supported behavior. Fields described as observed have an event/provider record; unknowns remain explicit. Offline checks need no credentials.

**References:** [Codex integration](architecture.md#codex-integration), [Documented interfaces](technical-discovery.md#documented-codex-interface-candidates), official app-server sections “Getting started,” “Start a turn,” and “Approvals.”

**Guards:** Do not build a second agent harness, confuse `turn/steer` with configurable new turns, or claim itemized costs from aggregate usage.

## Phase 3 — Build the evaluator and measure the routing opportunity

**How this serves the primary goal:** Establish trustworthy outcomes and discover whether configuration differences justify learned routing.

1. Build the Python runner around the shared TypeScript execution path. Pin tasks, repository commits, evaluator revision, images, architecture, limits, and artifact identifiers.
2. Run coding tools and evaluator code in the designated isolated environment. Validate patch application, known success/failure fixtures, clean regrading, and failure categories before buying model runs.
3. Run a small authorized fixed-configuration pilot on development tasks. Reuse valid records; repeat when variability or changed conditions warrants it.
4. Select strong fixed controls on development data. Examine the cost–success frontier and an explicitly retrospective oracle upper bound to diagnose headroom; the oracle is not deployable.
5. Use per-task cost and variance to size later collection/evaluation. Validate the multi-turn environment and stopping policy independently of the classifier.

**Output / done:** Each pilot result has a patch, executable outcome, manifest, and usage record. Recommend proceeding, narrowing the claim, adjusting the pool using development evidence, or pausing paid expansion for lack of routing opportunity.

**References:** [SWE-bench output](evaluation.md#swe-bench-output), [Multi-turn tasks](evaluation.md#multi-turn-tasks), [official evaluator guide](https://www.swebench.com/SWE-bench/guides/evaluation/).

**Guards:** No leaderboard substitution, host execution of untrusted benchmark code, favorable-task selection, or strong reliability claims from a tiny pilot. A negative pilot does not silently cancel fine-tuning; review the feasibility/cost trade-off with the owner.

## Phase 4 — Add classifier adapters and competitive controls

**How this serves the primary goal:** Isolate Jev's routing value before attributing improvement to project fine-tuning.

1. Implement transparent deterministic rules. Add a cheap learned control using the same permitted state and labels, such as TF-IDF plus a regularized linear classifier; paid embeddings are unnecessary initially.
2. Add hosted Jev and released OpenJev behind the typed-choice contract. Follow pinned examples linked in discovery/training and validate serialization, choice scoring, failures, and provenance.
3. Batch authorized development comparisons through the same harness, GPT pool, budgets, information policy, and evaluator. Batch OpenJev work to avoid idle hosting charges.
4. Establish matched precision, templates, and calibration procedure for the later untuned/tuned comparison. Record limitations on hosted-version control.

**Output / done:** Fixed, rules, hosted Jev, and untuned OpenJev have comparable execution paths; the cheap learned control is ready for Phase 5 labels. Classifier and switching overhead are included in totals.

**References:** [Strategies](evaluation.md#strategies), [Classifier dependencies](technical-discovery.md#classifier-dependencies), [Training plan](training-plan.md).

**Guards:** Do not change coding context when changing the router or substitute a rules demo for the classifier comparison.

## Phase 5 — Construct measured training data

**How this serves the primary goal:** Teach routes from executable outcomes rather than invented task-difficulty labels.

1. Measure candidate outcomes on predefined training states under a capped, development-informed sampling plan. Share collection across the cheap learned and OpenJev models.
2. Apply the reviewed correctness-first labels. Preserve ties, uncertainty, failed candidates, and all-failure states rather than forcing a successful winner.
3. Start with reproducible initial states. Add later-turn examples only when candidates can start from the same valid conversation and repository state. Disclose initial-only training if later-state replay is infeasible.
4. Audit duplicates, related issues, split isolation, leakage, option-position imbalance, and provenance. Freeze dataset and label-rule versions.

**Output / done:** Examples trace to measured outcomes and decision-time inputs. Held-out tasks have not influenced labels, prompts, configurations, or policies.

**References:** [Training data and leakage](evaluation.md#training-data-and-leakage-controls), [Outcome data and labels](training-plan.md#outcome-data-and-labels).

**Guards:** Different later trajectories are not interchangeable counterfactual states. A single lucky run is not proof of a generally superior route; repeat important ambiguous cases only within the cap.

## Phase 6 — Fine-tune OpenJev with bounded cloud compute

**How this serves the primary goal:** Deliver the requested specialized model and test whether adaptation repays its costs.

1. Finish checkpoint/helper inspection and select a supported adapter setup. Supervised option-token LoRA is the proposed first method; QLoRA depends on architecture/backward-pass compatibility. No reinforcement-learning loop is planned initially.
2. Compare current offers by expected completed-job cost, including setup, downloads, storage, evaluation, and shutdown. Verify availability before naming the cheapest suitable GPU.
3. Run one capped compatibility job: finite loss/gradients, frozen base and changing adapters, peak memory/step time, checkpoint save/reload, and valid option scores. Stop on failure; do not escalate hardware automatically.
4. Train a small predeclared candidate set within the cap. Select checkpoints/calibration on development data and report the selection budget. Match untuned/tuned inference conditions.
5. Compare coding outcomes as well as classification fit. Record checkpoint/tokenizer hashes, labels, hyperparameters, seeds, hardware, runtime, and total cost.

**Output / done:** A retrievable adapted checkpoint passes serving checks and has a controlled development comparison. Completing training does not establish better routing.

**References:** [Training plan](training-plan.md), including its compatibility gate and primary Transformers/PEFT references.

**Guards:** Do not infer training fit from an inference recipe, default to a large search, or silently replace the OpenJev checkpoint.

## Phase 7 — Freeze and evaluate the paper claims

**How this serves the primary goal:** Measure generalization under a protocol that cannot be adjusted to favor the router after final results are seen.

1. Freeze manifests, code, harness, GPT configurations, classifier prompts/checkpoints, policies, budgets, repetitions, failure handling, reliability margin, and analysis before held-out runs.
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
| Languages | Confirmed: TypeScript and Python | Review exact compatible runtime/dependency pins before setup. |
| Integration | Recommended: pinned app-server stdio, one execution path | Finish state/approval/usage contract; later bounded live proof. |
| Router output | Recommended: typed configuration choice and deterministic validation | Choose fields, fallback, timeout/retry rules, and context limits. |
| GPT pool | Proposed: two models × low/high | Verify access/execution and measure quality before naming winners. |
| OpenJev identity | Source identifies `openjev/openjev` 27B, independent of hosted Jev | Read exact pinned helper; confirm license suitability and adapter/readout behavior. |
| Training | Proposed supervised LoRA; QLoRA conditional | Verify backward pass/memory in a capped job before full training. |
| Benchmark | SWE-bench plus multi-turn study retained | Select cohort/version, container path, splits, and follow-up rules. |
| Reliability/statistics | Correctness first confirmed | Choose numeric margin, ambiguity policy, primary contrast, and affordable precision before final evaluation. |
| Funding | Owner reports $3,333 API credits; minimize consumption | Privately verify eligibility/expiry; authorize stage caps and separate cash compute before paid work. |
| Paper | Narrower empirical contribution proposed | Complete closest-method comparison; retain only supported claims. |

**Immediate next step:** Review Phase 0's integration, OpenJev training, and benchmark choices, then finish Phase 1's contracts. Do not begin another prototype while those choices are unresolved. Mid-turn routing, broad feature tasks, a public gateway, and unmotivated experimental expansion remain outside the initial scope.

# Evaluation and experiment records

Updated October 24, 2026. This is an experimental design, not a results report. Executable task checks determine correctness; the classifier and coding agent do not grade their own success. The full project includes SWE-bench, controlled multi-turn tasks, and qualitative stakeholder feedback.

## Research questions and claims

The owner selected this primary question: **Does fine-tuning OpenJev improve routing versus untuned OpenJev, producing better task performance or lower price/token usage?** Jev/OpenJev classifies each user prompt into a task type plus signals; a separate policy maps that classification to model/effort. The primary matched contrast changes the OpenJev weights while holding the taxonomy, downstream mapping, coding workflow, permitted information, and candidate configurations constant. Correctness remains the priority; report executable success and full cost together, with tokens as an additional resource measure.

Strong fixed configurations, rules, a cheap learned router, and hosted Jev establish whether either OpenJev variant is useful relative to simpler or external alternatives. Multi-turn adaptation and the separate effects of model/effort selection are secondary analyses, with claim-dependent controls. Fewer tokens across differently priced models need not mean a smaller bill.

Declare a primary comparison and reliability criterion before final evaluation. A low-cost prototype result does not establish an ML-paper contribution. [Research review](research-review.md) identifies close existing routing work and the narrower empirical contribution worth testing.

## Strategies

| Strategy | Purpose |
| --- | --- |
| Strong fixed GPT model/effort configuration | Competitive static control selected on development data, not an intentionally weak default. |
| Simple deterministic routing rules | Test whether Jev adds value beyond rules using the current prompt and common operational limits; no hidden access to history or failures. |
| Cheap learned classifier plus policy | Test whether current-prompt text features predict the same categories well enough under the shared mapping. |
| Hosted TypeSafe Jev plus policy | External category classifier under the shared mapping and coding workflow. |
| Released OpenJev, without project tuning, plus policy | Establish the independent checkpoint's category/routing behavior before our adaptation. |
| Fine-tuned OpenJev plus policy | Isolate category-classifier adaptation of that same parent checkpoint under a fixed shared mapping. |

The original five strategy families remain required; the cheap learned control strengthens the paper design. Train it using the same permitted states and category annotations as OpenJev, and share the downstream policy informed by measured configuration outcomes. Start without paid embeddings. Evaluate candidate fixed configurations on development tasks, select a strong primary fixed baseline, and preserve the development cost–success frontier. A broad trade-off claim should also compare appropriate low-cost and high-reliability fixed endpoints, or explicitly limit its scope.

Use the same GPT configuration pool, harness version, task inputs, available coding context, routing opportunities, tool permissions, stopping rules, and total resource limits. Keep classifier-specific formatting separate from information content. All strategies pay their own classification/switching overhead against the common limit; do not provide free extra coding attempts to an expensive router.

The owner selected prompt-only classification. Every matched classifier/rule control receives only the current user prompt as task content, with fixed category instructions where applicable. History, repository metadata/content, tools, prior failures, and progress summaries are excluded; user-pasted details in the current prompt are allowed. Codex retains its normal session/repository context across all arms. Evaluation metadata and identifiers must not enter classifier features. Automatic reliable fallback handles insufficient prompt information; count its usage and cost. A later context experiment must be separately specified and funded, and must preserve matched classifier inputs within each comparison.

The following controls become necessary for the corresponding claims, rather than an automatic full cross-product:

| Claim | Required comparison |
| --- | --- |
| Rerouting across developer messages improves outcomes | Initial-only selection versus selection at each new user prompt on the multi-turn set. |
| Joint selection beats selecting just one dimension | Model-only routing, effort-only routing, and joint routing with matched eligible settings. |
| Fine-tuning itself improves routing | Same OpenJev parent, taxonomy, serialization, precision, runtime/calibration settings, and frozen downstream mapping before/after adaptation. |
| Benefits come from routing rather than extra context | Matched context/handoff construction across fixed and routed strategies. |

Classification followed by a separate policy is the confirmed product. Direct configuration selection and internal-step routing are optional extensions. Internal-step routing is outside the initial product scope even if prior papers call those steps “turns.” A separately refitted mapping for each classifier is a distinct system comparison, not the primary isolated fine-tuning contrast.

## SWE-bench output

A standard issue-to-patch SWE-bench run tests selection at one initial user prompt. Multiple internal tool/model steps do not turn it into a test of adaptation across user prompts. Use it for initial routing and executable bug-fix quality; use the separate multi-turn protocol for adaptation claims.

Choose the dataset/version and sampling rule before collecting labels. The Phase 0 direction is a small pinned SWE-bench Verified development subset for the first pipeline pilot, using Python repositories and excluding pilot tasks/derivatives from final held-out evaluation. [SWE-bench Pro V2](https://labs.scale.com/leaderboard/swe_bench_pro_public_v2), whose dated September 22 update describes 642 tasks across 11 repositories, remains a candidate for a broader paper study. Feasibility, Python coverage, task quality, license, and compute cost must be checked before selecting the final cohort. Its page also describes older versions; do not mix those task counts or protocols.

Neither public collection is established here as contamination-free. A private split from a public benchmark prevents our own test-set tuning but cannot rule out model pretraining exposure. Training on one collection and testing on another introduces domain shift; report it separately from the effect of routing. Do not assume access to private benchmark tasks or a stakeholder's former employer's assets.

Pin task IDs, dataset revision, repository base commits, evaluator revision, container/image digests, CPU architecture, network policy, visible tool environment, and execution limits. Run the coding agent's repository commands inside the intended isolated environment as well as the official evaluator. Hidden checks/reference patches must not be accessible to the agent or classifier. Regrade the generated patch on a clean base so edits to tests cannot manufacture success.

The [official SWE-bench evaluator guide](https://www.swebench.com/SWE-bench/guides/evaluation/) describes prediction records with `instance_id`, `model_name_or_path`, and `model_patch`. Use distinct run identifiers and verify cache behavior. For another SWE-bench variant, follow that variant's pinned evaluator contract instead of assuming this command is interchangeable.

Retain patches, evaluator logs, and manifests for every attempt. Distinguish resolved tasks, incorrect patches, budget exhaustion, and infrastructure failures. Published leaderboard scores are contextual only: task subsets, harnesses, versions, limits, and costs differ. The main baseline is a rerun under our matched conditions. Hosted Jev classifies the task prompt, our policy selects a configuration, and a GPT coding model produces the patch in that arm. Pin the exact user-facing issue prompt; do not append repository/task metadata or hints to the classifier input.

## Multi-turn tasks

Create a small versioned scenario collection with pinned repositories, environments, sequences of user requirements, public/visible feedback rules, hidden checks, and maximum turns/time/cost. Example scenarios include a new constraint after an initial request, visible failing tests requiring diagnosis, a clarification invalidating an assumption, and an investigation followed by implementation.

Specify two kinds of user messages: required new information and corrective follow-ups. A strategy cannot skip a required future requirement and be credited as completing the whole scenario. At each stage, permit early completion under the same visible completion rule. Generate corrective follow-ups from a predeclared policy using only permitted visible evidence. Keep future prompts and hidden checks outside the agent's workspace and routing state.

Hidden evaluation verifies whether completion was actually correct; it must not become an oracle feeding error details or selecting the next route. If a visible completion criterion passes but hidden checks fail, record a failure rather than granting an extra hidden-test-driven repair opportunity. Define this controller behavior before writing scenarios. The router's own success declaration is never sufficient for credit.

Grade current requirements and regressions against earlier requirements. Record required messages, corrective messages, internal calls, and tools separately. A script that forces equal prompt counts cannot establish fewer needed follow-ups. Conversely, count shorter failed runs as failures, not as efficient completions.

Run each policy live from an independent state. Every route changes subsequent context, edits, and failures. Do not stitch together favorable steps from unrelated runs or use an offline hindsight oracle as deployable performance. Later-turn counterfactual labels require genuinely comparable saved states; final dynamic policy results require full live trajectories.

Scripted prompt counts measure this protocol. A stakeholder trial addresses usability, and actual human time savings would require an appropriate separate user study.

In the initial protocol, Jev sees only the current message, including vague corrective follow-ups. Preserve the defined follow-up text for all strategies; do not rewrite it into a fuller summary for one router. Results measure adaptation to new prompt content and operational constraints, not direct classifier access to execution progress. More informative context is a later ablation, not assumed free or automatically beneficial.

## Training data and leakage controls

Split training, development, and held-out tasks before examples or model-selection experiments. Keep related/duplicate issues, derived scenarios, and all turns of a task in the same split. Version the grouping procedure and manifest. If claiming transfer across repositories, hold out repositories where feasible and report the number of independent groups; ordinary task splitting alone does not establish that claim.

Use training tasks for labels and development tasks for policies, prompts, calibration, configurations, thresholds, and checkpoint selection. Do not repeatedly inspect held-out outcomes and adjust the system. Select the final pool and analysis before final runs. A materially changed protocol needs a new valid evaluation, not selective replacement of bad results.

Classifier training examples contain only the specific current prompt and category/signal annotations made from that same view. Later executable success, cost, and latency supply separate evidence for the routing policy, not semantic category labels or classifier features. Preserve uncertain category annotations, unknowns, outcome ties, and all-failure cases. Initial single-run configuration outcomes are noisy observations; use pilot evidence to target useful repetitions within budget. The complete proposed method is in [Training plan](training-plan.md).

A retrospective oracle can estimate attainable headroom among measured configurations on a development cohort. Label it as using future outcomes, quantify its selection bias/limited samples, and never compare it as a runnable router.

## Minimum records to implement

These are requirements for future schemas. Store raw private traces in controlled storage and commit reviewed manifests/aggregates. Stable identifiers must connect task, run, turn, decision, call, patch, and evaluator result.

| Record | Minimum useful fields |
| --- | --- |
| Task manifest | Source/version, task/group/split IDs, repo/base commit, image/evaluator revision, visible inputs, hidden-check references, follow-up policy, limits. |
| Experiment definition | Code/harness revision, strategy/policy/prompt versions, configuration pool, ordering/seeds/repetitions, caps, priced categories/date, analysis version. |
| Run | IDs, strategy, timestamps, completion/failure reason, patch hash, evaluator outcome/log reference, full cost/time, infrastructure status. |
| Classification | Current-prompt and serialized-input hashes, prompt-input policy and taxonomy/question versions, classifier/checkpoint version, predicted task-type/signal labels, per-field scores/unknowns/errors, question/pass count, latency, usage/cost source. |
| Routing decision | Classification reference, mapping version, eligible configurations, selected model/effort and fallback reason, limits/reservation, policy latency. |
| Coding usage/call | Requested/accepted/observed model and effort, available call IDs, tokens/categories, retry/error status, elapsed time, billed amount or estimate provenance. |
| Turn/progress | User-turn index, required versus corrective message, visible evidence, state/snapshot references, configuration changes, current/prior requirement outcomes. |
| Classification training example | Current-prompt reference, split/group metadata excluded from features, input/taxonomy versions, prompt-only category/signal annotations, review provenance, uncertainty/exclusion status. |
| Policy performance evidence | Source states/runs, split/group, measured candidate success/cost/time, category references, uncertainty/tie/all-failure status, mapping-construction version. |
| Training job | Base/tokenizer/helper/data revisions, objective/hyperparameters/seed, hardware/precision/runtime, peak memory, checkpoint/hash, validation and charged costs. |

Codex may expose aggregate turn/session usage rather than every internal request. Record the finest trustworthy granularity and its limits; do not invent complete call-level observability. Deduplicate cumulative events. Missing usage is unavailable, not zero. Provider reasoning tokens may already be included in output totals; follow the provider's billing semantics rather than double-counting them.

## Reporting and success criteria

Report resolved-task rate first. Predeclare an acceptable absolute success-rate loss, delta, for any noninferiority claim; “correctness first” does not yet specify a numerical tolerance. Report the paired success difference and an appropriate uncertainty interval. Such a claim requires its lower bound to meet the predefined margin. A nonsignificant difference is not evidence of equivalence, and a small pilot cannot certify reliability.

Use paired tasks across strategies. Treat each task/scenario and its repetitions/turns as a group, not independent samples. A task-block bootstrap is a candidate analysis; preserve repository structure where the generalization claim and number of repositories support it. Select the exact interval/test, confidence level, primary comparison, handling of repeated runs, and secondary/multiple comparisons before final evaluation. Use development variance and desired precision to plan an affordable sample. If the cap is too small, label the result exploratory and narrow the claim.

Report mean/total inference cost across all attempted tasks, cost per resolved task as total cost divided by total resolved tasks, and uncertainty. The latter is undefined when no tasks are resolved; do not report zero. Include failed attempts, retries, classifier inference, switching/context/cache overhead, and final validation calls actually made by the agent. Keep time to first response separate from end-to-end completion time, including classification and tool execution.

Also report tokens, latency distribution, fallback/error rates, corrective follow-ups, and regressions. Report category agreement on independently reviewed labels where available, unknown rates, category/route changes after tuning, and per-question classifier overhead. Classification agreement is a diagnostic; executable success and cost remain primary. Use common stop limits and a predeclared policy for service outages and infrastructure reruns. Reruns have new IDs and remain in operational cost records. Balance strategy order to reduce time/provider effects; document model alias or service changes.

Separate actual billed usage from price-equivalent estimates, credit consumption, subscription quota, and cash payments. Track label collection, checkpoint selection, training, endpoint uptime, storage, and benchmark CPU/GPU separately from deployment inference. Report one-off and recurring costs and a conditional break-even analysis if inference savings are positive. Warm request latency alone does not capture endpoint startup or idle hosting expenses.

Freeze claims to the evidence: better option prediction, lower inference cost, noninferior success, joint-selection gains, multi-turn gains, and human productivity are distinct statements. A careful neutral or negative study can complete the research. No savings threshold, final sample size, or performance improvement has yet been established.

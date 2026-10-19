# Evaluation and experiment records

The main output is executable coding-task evidence: patches, evaluation outcomes, and cost/time comparisons for the same tasks under different routing strategies. Routing success must be assessed through the coding agent's results, not the classifier's self-rating.

## Strategies

| Strategy | Purpose |
| --- | --- |
| Strong fixed GPT model/effort configuration | Establish a competitive static baseline selected on development data |
| Simple deterministic routing rules | Test whether a classifier improves over obvious task/progress signals |
| Hosted TypeSafe Jev router | Compare an external hosted decision model using the shared coding harness |
| Untuned OpenJev router | Establish the base checkpoint's routing performance |
| Fine-tuned OpenJev router | Measure the effect of tuning that same base model |

Use the same eligible GPT configurations, Codex harness/version, tasks, routing opportunities, limits, and decision-time information for each strategy. Different classifier prompts or adapters must not receive privileged evaluation data. Select and freeze baseline configurations and policy settings using development data.

Model-only routing, effort-only routing, direct-selection versus feature-based policy, and initial-only versus repeated routing were discussed as possible research extensions. They are not all mandatory initial experiment arms. Mid-turn checkpoint adaptation is also outside the agreed core scope. [Research hypotheses and extensions](research-notes.md) preserves each comparison's purpose and distinguishes these additional experiments from the core classifier comparison.

## SWE-bench output

Choose and document a manageable official SWE-bench variant/subset, task IDs, dataset revision, repository base commits, environment/evaluation versions, and resource limits. Verify the current evaluator requirements before choosing compute. The coding agent generates patches; the benchmark evaluator applies them and runs its checks in the required isolated environment.

Retain patch artifacts and evaluator reports/logs for each run in suitable storage. A comparison report should summarize resolved tasks, failures, total cost, tokens, completion time, and overhead by strategy, with links or hashes connecting each result to its run artifacts. Hidden evaluation information must remain outside the router and coding agent's allowed inputs.

Published leaderboard scores provide context. Different model versions, task subsets, harnesses, limits, and evaluation conditions prevent treating a leaderboard difference as a controlled measurement of this router. The main comparison reruns the chosen strategies under common conditions. Hosted Jev routes; the selected GPT coding agent produces the SWE-bench patch in that arm too.

## Multi-turn tasks

Create a smaller reproducible task set with pinned repositories, environments, permitted follow-up inputs, executable checks, and maximum turns/time/cost. Possible scenarios include a simple request gaining a difficult requirement, a failed implementation needing diagnosis, a clarification changing an assumption, or an investigation followed by straightforward implementation. These scenarios have not been authored yet.

Use a consistent follow-up policy that permits earlier successful completion. Forcing every strategy to receive the same fixed number of prompts cannot demonstrate fewer required corrective follow-ups. Keep hidden checks private; specify which ordinary visible test failures the agent may use. Separate task-completion turn count from internal tool/model call counts.

Evaluate adaptive policies live. Do not estimate a router's performance by stitching successful steps from unrelated recorded trajectories, because each route changes the subsequent state. Report truncated, failed, timed-out, and budget-exhausted tasks alongside successes. Stakeholder feedback addresses usability; it does not replace executable correctness or prove human time savings from scripted prompt counts.

## Training data and leakage controls

Split training, development, and held-out evaluation tasks before constructing routing examples. Keep turns from the same task together and account for related/duplicate tasks when defining splits. Record the split manifest and revisions. Do not tune the router, configuration pool, prompts, reliability tolerance, or baselines on held-out outcomes.

Measure candidate configurations on training/development tasks to construct labels that prioritize correctness and then cost/time among similarly reliable choices. A single noisy run does not establish a universally best configuration. The repetition policy, label rule, and definition of similarly reliable need to be fixed using the affordable development pilot.

Training examples may pair decision-time observations with later measured labels, but future outputs and hidden checks are labels/evaluation material only, never classifier input. For later-turn comparisons, preserve the exact reproducible pre-decision state when testing alternative routes; do not treat different trajectories as if they were the same state. Start with initial-prompt examples if later-turn state replay is not yet reliable.

Keep the untuned checkpoint fixed, record the tuned checkpoint's parent/version and training recipe, and freeze the policy before final evaluation. Full fine-tuning versus an adapter method, target labels, dataset size, and cloud hardware remain open.

## Minimum records to implement

These are proposed record requirements, not an implemented schema. Assign stable IDs so outcomes and costs can be traced back to a task, run, turn, and model call. Store raw private traces locally or in controlled artifact storage; commit reviewed manifests and aggregates only.

| Record | Minimum useful fields |
| --- | --- |
| Task manifest | Task ID, source/dataset revision, split, repository/base commit, environment version, visible inputs, evaluator/check references, follow-up policy, limits |
| Experiment definition | Experiment ID, code revision, harness version, strategy/policy versions, model pool, seeds/repetitions, resource caps, pricing reference/date |
| Run | Run ID, task/experiment IDs, strategy, start/end times, termination reason, final patch reference/hash, evaluator result/reference, total cost and timing |
| Routing decision | Run/turn ID, timestamp, bounded input reference/hash, classifier/checkpoint version, selected configuration, fallback reason, classification latency and usage |
| Coding call | Run/turn/call IDs, requested and observed model/effort, request status, usage categories exposed by the provider, cost source, elapsed time, retries/errors |
| Turn/progress | User-turn index, permitted prompt/context references, visible progress/failures, corrective-follow-up count, configuration changes |
| Training example | Source task/run/state IDs, split, input/features available at decision time, measured candidate outcomes, label/ranking, label-rule version |
| Training job | Base checkpoint and dataset revisions, method/hyperparameters/seed, hardware/runtime, checkpoint reference/hash, validation results, total training cost |

Token categories can overlap across providers. Use provider-reported totals and billing semantics; do not double-count reasoning tokens if they are already included in output usage. Record missing usage as unavailable rather than zero. Include classification, failed attempts, retries, and additional calls caused by switching in inference cost. Track training, hosting, and benchmark execution separately and include them when discussing overall project economics.

## Reporting and success criteria

Report task success first, then total inference cost and completion time, plus token use, corrective follow-ups, classifier latency, fallback/retry rates, and regressions across turns. Distinguish per-task totals from cost per successful task, and include all attempted runs in the latter calculation. Keep time to first response separate from time to a correct completed task.

Use paired tasks and suitable repetitions to report uncertainty at the task level; do not count correlated turns as independent tasks. The exact uncertainty method, repetition count, and allowable success-rate difference remain open. Freeze those choices before held-out evaluation. A neutral or negative result should be reported honestly; no savings threshold or performance gain has been established.

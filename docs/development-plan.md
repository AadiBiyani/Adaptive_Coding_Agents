# Development plan

The sequence below turns the agreed proposal into a small measurable system. These are proposed implementation steps, not additional course milestone requirements. Obtain the actual Milestone 2/3 instructions separately when preparing those submissions.

## 1. Verify the integration and define the pilot

Read the context documents, inspect the installed Codex version, and verify the current official session and per-turn model/effort interfaces. Choose a minimal language/runtime based on that interface. Record the exact versions and the expected terminal workflow in `docs/architecture.md`.

Select a small candidate GPT configuration pool and a tiny development pilot. Roughly two or three models with four to six supported combinations was an early sizing suggestion, not a locked requirement. Verify access and actual supported settings before selecting exact IDs. Identify current API-credit availability and expiry, then agree a pilot API cap and separate cash-compute cap before any paid runs.

Completion means a documented integration choice, valid proposed configurations, explicit caps for any live work, and a reproducible pilot definition. Free read-only inspection and offline design can proceed while budget decisions remain open.

## 2. Implement the terminal and session foundation

Build a minimal client that accepts a prompt, obtains a configuration from a stub/fixed policy, executes a Codex turn, and accepts a follow-up in the same session. Add a bounded context builder, explicit supported-configuration validation, fallback behavior, stopping limits, and structured usage/decision records.

Verify offline orchestration first. An authorized small live check must demonstrate that a model/effort change takes effect without losing relevant conversation/repository context. Preserve ordinary coding tools and approval behavior. Completion is a working two-turn workflow and meaningful checks for session continuity, setting application, fallback, and accounting.

## 3. Establish the benchmark runner and fixed baselines

Pin a SWE-bench subset and reproducible environment; separate task splits before data collection. Run the same harness with fixed configurations, collect patches and evaluator outcomes, and aggregate correctness, cost, and time. Start at pilot scale and use its measured cost to estimate a larger study.

Completion means repeatable task execution, artifact-to-result traceability, real usage records, and an evidence-based fixed baseline selected on development data. A runner that merely asks a model whether it succeeded does not meet this criterion.

## 4. Add routing strategies

Implement simple rules, hosted Jev, and untuned OpenJev behind the same decision interface and valid configuration registry. Keep decision inputs and routing opportunities comparable. Measure classifier latency, overhead, fallback behavior, and end-to-end outcomes on development tasks.

Completion means each strategy can run through the same harness and benchmark workflow, with failures and usage attributable to the correct component. Do not claim tuning gains until the untuned comparison exists.

## 5. Collect examples and fine-tune OpenJev

Choose a training objective and label rule based on observed candidate outcomes and the correctness-first priority. Use only training/development material, preserve reproducible decision states, and estimate example-collection cost. Verify the current checkpoint/license, training support, and hardware requirements before selecting the cheapest suitable cloud option.

Run a small authorized training smoke test, then a bounded training job if it works. Record the recipe, dataset/checkpoint revisions, training cost, and development validation. Completion means a reproducible tuned checkpoint and a direct untuned-versus-tuned comparison; a rented GPU alone is not a deliverable.

## 6. Freeze and evaluate

Finalize the held-out task list, eligible configurations, selection rules, success-rate tolerance, repetitions, and stopping budgets before evaluating. Run all agreed strategies live on SWE-bench and the small controlled multi-turn set. Keep held-out outcomes out of further model or policy selection for this evaluation.

Completion means patches and executable evaluation records, a comparable results table with uncertainty, total cost/time accounting, and documented failure cases. Report any changes to the protocol or missing conditions explicitly.

## 7. Obtain workflow feedback and report results

Give the stakeholder a usable bounded trial, collect authorized qualitative feedback, and document the comparison's limitations. Keep private feedback records outside this public repo unless publication is explicitly authorized. Produce installation/use instructions, reproducible experiment commands, and a report explaining when routing helped or hurt.

Completion means the terminal workflow can be used, the trained classifier can be reproduced or retrieved with its provenance, and the results support appropriately narrow conclusions. No guarantee of savings or improved quality is required to report a sound experiment.

## Open decisions

| Decision | Resolve by |
| --- | --- |
| Related-work comparisons and selection of optional research experiments | Before expanding the experiment matrix or claiming novelty |
| Codex interface/version and implementation language | Integration spike |
| Exact GPT models, supported reasoning settings, and fallback | Pilot configuration |
| API pilot cap, total execution caps, and cash-compute limits | Before paid runs |
| SWE-bench variant/subset, environments, and split grouping | Before collecting examples |
| Classifier output labels, policy, and tuning target | Development data design |
| Numerical reliability tolerance and repetition policy | Before final evaluation |
| Fine-tuning method, GPU provider, hosting, and checkpoint storage | Training smoke test |
| Multi-turn follow-up protocol and hidden-check handling | Before multi-turn execution |
| Later course deliverables and deadlines | When their official instructions are available |

Record decisions and evidence as they are resolved, then update `HANDOFF.md` with the next unfinished step. Do not repeatedly ask the owner to reconfirm the agreed terminal workflow, bug-fixing scope, fine-tuning goal, correctness priority, or SWE-bench deliverable.

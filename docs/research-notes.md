# Research hypotheses and extensions

The owner supplied this background proposal from another project conversation on October 19, 2026. It motivates the joint-selection research question and preserves useful experiments beyond the initial Milestone 1 scope. It does not establish working APIs, measured gains, or novelty.

The October 24 [Research review](research-review.md) now checks primary sources and narrows the proposed contribution. [Development plan](development-plan.md) is authoritative for active work; this background does not revive the inactive course schedule or expand the implementation scope.

## Research question and contribution

Can a lightweight decision model allocate models and reasoning effort throughout a coding task to reduce total cost while maintaining task success?

The proposed contribution is a controlled study of joint model and reasoning selection during executable coding workflows, including whether adapting to visible progress improves the cost–success trade-off. In the agreed initial version, adaptation occurs at new user-prompt boundaries. Internal execution checkpoints are a possible extension.

The three central pieces are a classifier that judges task/progress signals, a routing policy that combines those signals with measured configuration performance and remaining limits, and a benchmark suite that evaluates correctness, cost, latency, and reliability. A coding harness still owns the conversation, repository, tools, edits, and test execution; model access alone does not provide that harness.

## Hypotheses for task-dependent routing

| Situation visible at decision time | Candidate behavior to test |
| --- | --- |
| Localized, well-understood change | Choose a cheaper model with less reasoning |
| Difficult diagnosis with conflicting evidence | Increase reasoning on the current model |
| Repeated unsuccessful attempts | Switch to another eligible model |
| Implementing an already established solution | Reduce reasoning effort |
| Classifier cannot make a usable decision | Use the predefined valid fallback |

These are experimental hypotheses, not facts about which model is best. Measure model and effort jointly: a cheaper model with more reasoning could outperform a stronger model with less reasoning, or the reverse. The supported-configuration registry must represent the actual controls for each candidate.

The original proposal considered the current request, repository context, execution phase, visible tool results, previous failures, progress, and budgets. The later Phase 1 decision restricts classifier task content to the specific current prompt, with fixed category instructions. These broader classifier inputs are optional future research, not the active contract. The policy still uses configuration availability and remaining budgets, and Codex retains its coding session. Hidden checks, reference patches, and future outcomes remain forbidden classifier inputs in any variant.

## Alternative ways to select a configuration

Direct selection gives Jev descriptions of the eligible configurations and their measured development capabilities, then asks for a configuration choice. Classification followed by a policy asks for task/progress signals and uses rules or a small trained predictor to map them to a route. Both need the same information, valid configuration pool, and execution limits to make the comparison meaningful.

The owner clarified the initial contract during Phase 1: Jev/OpenJev predicts a task type plus a few signals, and a separate policy chooses the configuration. This supersedes the earlier direct-choice recommendation. Keep category annotations separate from measured configuration outcomes and hold the mapping fixed in the primary tuned/untuned comparison. Direct choice remains an optional later ablation. Category confidence is not automatically the probability that a chosen configuration will solve the task; validate any confidence-based policy against observed routing outcomes.

## Additional comparison arms

| Comparison | Question it addresses |
| --- | --- |
| Model selection with effort held fixed | How much value comes from choosing the model? |
| Effort selection with model held fixed | How much value comes from choosing the reasoning setting? |
| Joint model and effort selection | Does choosing the combination help beyond either choice alone? |
| Initial-only selection versus selection at new user prompts | Does adaptation across user turns help? |
| User-prompt routing versus internal checkpoints | Does reacting during execution justify its added complexity and cost? |
| Direct selection versus classification plus policy | Is it better to ask the classifier for a route or for signals used by a policy? |

The strong fixed configuration and simple-rule baseline remain important controls, with a cheap learned control added for the paper study. These arms complement the hosted Jev/untuned OpenJev/fine-tuned OpenJev comparison and do not require every cross-product. Initial-only versus per-user-turn selection is required if we claim an adaptation benefit; model-only and effort-only controls are required if we claim joint selection beats either alone. Other extensions remain optional. Select affordable experiments after the pilot and narrow claims when an ablation is unaffordable.

For any future checkpoint extension, define routing opportunities in advance, such as after investigation or failed visible tests. Keep the handoff representation constant initially and run each adaptive policy live. Do not estimate performance by combining favorable pieces of unrelated trajectories.

## Scope decisions made after the original proposal

| Original proposal | Agreed development scope |
| --- | --- |
| General coding-model choice | GPT coding models first, with cost-conscious use of the owner's existing credits |
| Routing throughout execution | Routing at each new user prompt first; internal checkpoints later |
| Platform supplies classification and coding calls | Preserve a Codex terminal workflow through a dedicated command; verify provider/billing compatibility |
| Jev as classifier | Compare hosted TypeSafe Jev, untuned independent OpenJev, and cloud-fine-tuned OpenJev |
| General cost/success trade-off | Correctness first, then lower cost/time among similarly reliable choices |
| SWE-bench plus multi-turn tasks | Retained as central outputs, with qualitative stakeholder usability feedback |

The original build order emphasizes a benchmark runner, a small fixed-configuration pilot, initial routing, checkpoints, and held-out evaluation. The current development plan first verifies the Codex integration, then establishes the same runner/baseline foundation, adds classifier comparisons and fine-tuning, and evaluates the frozen policy. Checkpoint routing stays optional.

## Related work and platform leads

The supplied proposal names OpenRouter's Decisions and System One APIs as possible Jev access paths and mentions reasoning controls that differ by model. Verify current documentation, availability, and billing before choosing an integration. Access to GPT models through another provider does not demonstrate that the owner's direct API credits will pay for those calls.

The proposal also identifies automatic routing, a Jev routing experiment, and HRBench. The [Research review](research-review.md#related-work-and-the-claim-it-permits) now records specific versions of RouteLLM, Ares, SWE-Router, CodeRescue, Control the Harness, Scrouting, and HRBench. Their overlap makes a broad novelty claim inappropriate. Complete a closer method comparison before choosing final claims; frame the contribution around live executable evidence, controlled classifier adaptation, and total economics.

The stakeholder can help choose realistic debugging tasks, define an acceptable reliability trade-off before final evaluation, and assess whether results would change his workflow. Those conversations and trials are future work, not completed feedback.

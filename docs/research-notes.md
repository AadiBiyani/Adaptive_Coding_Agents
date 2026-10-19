# Research hypotheses and extensions

The owner supplied this background proposal from another project conversation on October 19, 2026. It motivates the joint-selection research question and preserves useful experiments beyond the initial Milestone 1 scope. It does not establish working APIs, measured gains, or novelty.

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

Inputs can include the current request, relevant repository context, investigation/implementation/validation phase, visible tool results, previous failed attempts, observed progress, and remaining budgets. At a new user turn, only information already available at that point is eligible. No hidden test outcomes, future progress, or inaccessible repository information may leak into the decision.

## Alternative ways to select a configuration

Direct selection gives Jev descriptions of the eligible configurations and their measured development capabilities, then asks for a configuration choice. Classification followed by a policy asks for task/progress signals and uses rules or a small trained predictor to map them to a route. Both need the same information, valid configuration pool, and execution limits to make the comparison meaningful.

The initial implementation can choose one contract and keep the adapter/policy boundary flexible. Comparing both approaches is an additional experiment. Classifier confidence is not automatically the probability that a chosen configuration will solve the task; validate any confidence-based policy against observed routing outcomes.

## Additional comparison arms

| Comparison | Question it addresses |
| --- | --- |
| Model selection with effort held fixed | How much value comes from choosing the model? |
| Effort selection with model held fixed | How much value comes from choosing the reasoning setting? |
| Joint model and effort selection | Does choosing the combination help beyond either choice alone? |
| Initial-only selection versus selection at new user prompts | Does adaptation across user turns help? |
| User-prompt routing versus internal checkpoints | Does reacting during execution justify its added complexity and cost? |
| Direct selection versus classification plus policy | Is it better to ask the classifier for a route or for signals used by a policy? |

The strong fixed configuration and simple-rule baseline remain important controls. These optional arms complement the core hosted Jev/untuned OpenJev/fine-tuned OpenJev comparison; they do not replace it or mandate every cross-product of settings. Select affordable experiments after the pilot.

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

The proposal also identifies OpenRouter automatic routing, a published Jev routing experiment, and HRBench work on thinking-mode selection as related-work leads. Exact publications, versions, and overlap have not been established in this repository. Locate and read their primary sources before claiming novelty or choosing literature baselines. Frame the contribution around the measured coding workflow and controlled comparisons rather than claiming to invent model routing.

The stakeholder can help choose realistic debugging tasks, define an acceptable reliability trade-off before final evaluation, and assess whether results would change his workflow. Those conversations and trials are future work, not completed feedback.

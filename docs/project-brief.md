# Project brief for development

This is the development summary of the agreed Milestone 1 proposal. The exact stakeholder-reviewed brief, approval records, and personal validation evidence remain in the private course submission package.

## Product value case

The stakeholder is a developer with applied AI and multi-turn coding-benchmark experience. He rarely chooses coding models based on the task because he does not know which configuration is most suitable. He mainly uses cheaper models when fanning out subagents. He wants to explore agent harnesses and improve his Codex terminal workflow while reducing corrective prompts, completion time, and model cost.

The proposed product is a routing component accessed through a dedicated terminal command. On each newly submitted prompt, a Jev or OpenJev classifier examines the prompt and bounded available conversation and repository context. A policy maps its output to a valid GPT model and reasoning-effort configuration before the coding turn starts. The workflow must preserve the repository, tools, approvals, and conversation needed to finish the task.

The initial scope is repository bug fixing and debugging. The intended deliverables are a usable router, a cloud-fine-tuned OpenJev classifier, and an evaluation report containing SWE-bench results and strategy comparisons. A small reproducible multi-turn evaluation examines corrective follow-ups, and a stakeholder trial supplies qualitative usability feedback. Feature development, general refactoring, and routing at internal checkpoints are later extensions.

The priority is correct task completion, followed by lower cost and time among similarly reliable configurations. Routing could add latency or make worse choices; savings and quality improvements are hypotheses to test. Reducing the number of prompts means reaching a correct task outcome with fewer corrective user follow-ups, not reducing the number of benchmark tasks.

## Engineering credibility checks

Useful routing requires meaningful differences between available model/effort configurations and enough information in the current prompt and context to choose among them. The project will first verify the Codex integration and measure fixed configurations on development tasks. A registry will represent actual supported configurations rather than assuming every model offers interchangeable low/high/off settings.

The model comparison will include a strong fixed GPT configuration, simple routing rules, hosted TypeSafe Jev, untuned OpenJev, and fine-tuned OpenJev. Hosted Jev and OpenJev are separate models. The untuned/tuned OpenJev comparison isolates additional training on the same base checkpoint. The coding harness, task set, eligible configurations, routing opportunities, and execution limits must be shared across strategies.

Training targets will come from measured coding outcomes. Training, development, and held-out evaluation tasks will be separated, with related turns kept together. Router inputs must contain only information available before the routing decision. The learned model and selection policy will be frozen before held-out evaluation. Executable checks will determine task success.

SWE-bench will evaluate generated patches on a documented subset. The multi-turn protocol will define follow-up behavior, stopping limits, and executable success checks, allowing earlier completion when a strategy succeeds. Results will include failures and exhausted budgets, repeated runs where affordable, and uncertainty estimates. Scripted prompt counts alone cannot establish human time savings.

The owner reported $3,000 of GPT API credits in September 2026 and explicitly wants to minimize their use. This is a historical available balance, not an allocation or a verified current balance. Cloud fine-tuning, classifier hosting, and benchmark execution have separate costs; their spending caps are undecided. Spending limits will be set before paid runs. Local development hardware reported during planning is a MacBook Pro with an Apple M5 and 16 GB memory. Training is planned for cloud compute; the cheapest suitable setup must be selected using current requirements and prices.

The main risks are weak or overfit routing, overhead that outweighs savings, and integration or training demands that exceed the semester resources. A small pilot, explicit fallback, controlled evaluation, and phased implementation will help assess these risks early. Exact model IDs, task counts, numerical reliability tolerances, cloud provider, and training method remain implementation decisions.

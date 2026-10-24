# Project brief for development

This is the development summary of the agreed Milestone 1 proposal. The exact stakeholder-reviewed brief, approval records, and personal validation evidence remain in the private course submission package.

## Product value case

The stakeholder is a developer with applied AI and multi-turn coding-benchmark experience. He rarely chooses coding models based on the task because he does not know which configuration is most suitable. He mainly uses cheaper models when fanning out subagents. He wants to explore agent harnesses and improve his Codex terminal workflow while reducing corrective prompts, completion time, and model cost.

The proposed product is a routing component accessed through a dedicated terminal command. On each newly submitted prompt, a Jev or OpenJev classifier examines the prompt and bounded available conversation and repository context. A policy maps its output to a valid GPT model and reasoning-effort configuration before the coding turn starts. The workflow must preserve the repository, tools, approvals, and conversation needed to finish the task. The OpenRouter analogy means a common routing entry point; a public gateway or billing platform is outside the initial product.

The initial scope is repository bug fixing and debugging. The intended deliverables are a usable router, a cloud-fine-tuned OpenJev classifier, and an evaluation report containing SWE-bench results and strategy comparisons. A small reproducible multi-turn evaluation examines corrective follow-ups, and a stakeholder trial supplies qualitative usability feedback. Feature development, general refactoring, and routing at internal checkpoints are later extensions.

The priority is correct task completion, followed by lower cost and time among similarly reliable configurations. Routing could add latency or make worse choices; savings and quality improvements are hypotheses to test. Reducing the number of prompts means reaching a correct task outcome with fewer corrective user follow-ups, not reducing the number of benchmark tasks.

## Engineering credibility checks

Useful routing requires meaningful differences between available model/effort configurations and enough information in the current prompt and context to choose among them. The project will first verify the Codex integration and measure fixed configurations on development tasks. A registry will represent actual supported configurations rather than assuming every model offers interchangeable low/high/off settings.

The model comparison will include a strong fixed GPT configuration, simple routing rules, a cheap learned control, hosted TypeSafe Jev, untuned OpenJev, and fine-tuned OpenJev. Hosted Jev and OpenJev are separate models. The untuned/tuned OpenJev comparison isolates additional training on the same base checkpoint under matched inference conditions. The coding harness, task set, eligible configurations, routing opportunities, and execution limits must be shared across strategies.

Training targets will come from measured coding outcomes. Training, development, and held-out evaluation tasks will be separated, with related turns kept together. Router inputs must contain only information available before the routing decision. The learned model and selection policy will be frozen before held-out evaluation. Executable checks will determine task success.

SWE-bench will evaluate generated patches on a pinned cohort and evaluator. Standard issue-to-patch runs measure initial selection, so a separate multi-turn protocol is needed to test adaptation across user prompts. That protocol will distinguish required new information from corrective follow-ups, define stopping rules, and withhold hidden checks from routing inputs. Results will include failures and exhausted budgets, repeated runs where affordable, and uncertainty estimates. Scripted prompt counts alone cannot establish human time savings.

The owner reports $3,333 of OpenAI API credits as of the October 2026 planning update, superseding the earlier $3,000 estimate, and wants minimal use for necessary validation, class submissions, and ML-paper experiments. This is not an allocation or independently verified balance. Cloud fine-tuning, hosted classification, and benchmark execution have separate costs; stage caps remain undecided. Routine development should use offline checks and included development tooling where suitable. Local hardware reported during planning is a MacBook Pro with an Apple M5 and 16 GB memory. Fine-tuning is planned on cloud compute; hardware selection requires a compatible recipe, measured memory, and a capped total-job estimate.

The stack is TypeScript for the terminal/router/Codex integration and Python for training, benchmarking, and analysis. The roadmap recommends one shared coding execution path, a small GPT configuration pool, and supervised OpenJev adapter training after feasibility checks. The owner requested removal of the premature prototype and a coherent requirements review before further coding; the Milestone 2 schedule is now inactive.

The owner intends to develop an ML paper. Existing work already studies coding-agent routing and reasoning allocation, so the contribution must be narrower and supported by controlled evidence. Strong controls, held-out data, a predefined reliability margin, paired uncertainty, and training/hosting economics are part of the research plan. The main risks are weak routing signal, overfitting, overhead that outweighs savings, and integration or training costs that exceed resources. Final configurations, cohort sizes, numerical reliability criteria, cloud provider, and verified training pins remain open; neutral or negative results are valid outcomes.

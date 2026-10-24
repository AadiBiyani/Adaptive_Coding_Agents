# Research and technology review

Reviewed October 24, 2026. These are source-backed findings and design recommendations, not implementation results. The review is sufficient to improve the plan, but it is not an exhaustive novelty search or a guarantee of publication.

## Recommendation

Build a small TypeScript routing layer around the Codex harness, with Python for data collection, OpenJev adaptation, and executable evaluation. Start with a restricted GPT model/effort pool. Measure whether there is a useful routing opportunity before expanding training or evaluation. Keep the complete project independent of the archived Milestone 2 schedule.

“Like OpenRouter” means one routing entry point and interchangeable configurations. A public gateway, hosted multi-user service, billing platform, dashboard, or full OpenAI-compatible API is not needed to test this research question.

## Related work and the claim it permits

| Primary source | Relevant evidence | Consequence for this project |
| --- | --- | --- |
| [RouteLLM, v3](https://arxiv.org/html/2406.18665v3), §§2–4 and Appendix B | Learned model routing and contamination considerations precede this project. | Include a cheap learned predictor; the existence of a router is not novelty. |
| [Ares, v1](https://arxiv.org/html/2603.07915v1), §3 and §4 | Selects reasoning effort at internal agent steps using learned routing. | Adaptive reasoning effort is established; distinguish user-message boundaries from agent/tool steps. |
| [SWE-Router, v1](https://arxiv.org/html/2607.00053v1), §§3–5 | Uses a partial coding trajectory to choose whether to continue cheaply or restart with a stronger model. | Coding routing using progress is established. Our retained session and routing boundary must be explicit. |
| [CodeRescue, v1](https://arxiv.org/html/2607.19338v1), §§3 and 5 | Learns recovery decisions from executable outcomes after a failed attempt. | Failure-aware routing and outcome labels alone are not new contributions. |
| [Control the Harness, Control the Cost, v1](https://arxiv.org/html/2609.28919v1), §§4.5–4.9 | Uses Jev classifications, discusses effort, and reports an emulation driven by measured behavior. | Close conceptual overlap. A live executable study could add evidence, but do not describe that paper's emulation as the same evaluation. |
| [Scrouting, v1](https://arxiv.org/html/2608.04804v1), §§6–7 | Its cheapest-fixer-plus-handoff control matches its routing result. | Hold context and handoff construction constant; test incremental value attributable to routing. |
| [HRBench, v1](https://arxiv.org/html/2605.28398v1), §4 and Appendix D | Studies thinking-mode strategies under common conditions and model-specific settings. | Effort controls differ; isolate model selection, effort selection, and their combination when making joint-selection claims. |

Proposed contribution: a controlled executable comparison of hosted Jev, released OpenJev, and task-adapted OpenJev for joint GPT model/effort selection at developer-message boundaries, including whether later-message adaptation repays classification, switching, and training costs.

That contribution is a hypothesis to refine against the closest methods. A product integration can be useful even if the paper ends up as a careful empirical study rather than a new routing algorithm. Never label the project “first” without a much stronger literature review.

## Stack decision

| Layer | Recommendation | Reason and boundary |
| --- | --- | --- |
| Terminal client and router | TypeScript in strict mode | Matches the user's stack requirement and permits one typed policy implementation shared by interactive and benchmark clients. |
| JavaScript runtime/tooling | Node.js 24 LTS, npm lockfile, TypeScript compiler | A small single package is enough initially. [Node's release table](https://nodejs.org/en/about/previous-releases) lists 24 as LTS on the review date; the locally observed 26.3.1 is not the proposed pinned runtime. |
| Codex integration | Version-pinned app-server via stdio, generated protocol types | The [official app-server](https://learn.chatgpt.com/docs/app-server) targets clients needing conversation history, approvals, and streamed events. Version-matched schemas take precedence over copying incompatible examples. |
| Python work | Python 3.12 candidate, uv lockfiles; separate training and evaluator environments | Keep benchmark dependencies independent of GPU/CUDA serving libraries. Python patch versions and exact compatible library pins must be resolved before installation. [uv project documentation](https://docs.astral.sh/uv/concepts/projects/) describes its lock/sync workflow. |
| Training | PyTorch, Transformers, PEFT; supervised adapters first | Use explicit option-choice supervision. QLoRA and GPU fit are candidates requiring verification, not established facts. |
| Evaluation | Official task evaluator in isolated Linux containers; Python orchestration and analysis | Preserve the benchmark's grading semantics. The Python runner invokes the same TypeScript execution path used by the terminal. |
| Storage and contracts | Versioned JSON Schema, JSONL records, hashed manifests; Parquet only if useful for analysis | Avoid an unnecessary database, queue service, or observability subscription in the first study. |
| Verification | TypeScript typechecking and offline protocol tests; pytest for Python data/evaluator logic | Paid inference should not be needed for routine regression checks. Select concrete test dependencies only when the design gate closes. |

The [Codex SDK guide](https://learn.chatgpt.com/docs/codex-sdk) recommends the SDK for automated jobs and app-server for custom interactive clients. We choose the latter as the common execution path to avoid evaluating a different harness from the product. A Python SDK exists, but adding a second Codex client implementation would make controlled comparisons harder.

## Proposed GPT configurations

Use a two-model, two-effort grid if all four configurations are accessible through the pinned Codex integration. These are candidates, not measured best routes or an authorized experiment.

| Model candidate | Efforts to compare | Standard input/output USD per million tokens |
| --- | --- | --- |
| [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna) | low, high | 0.10 / 0.50 |
| [gpt-6.1-sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) | low, high | 2.00 / 10.00 |

Both model pages document these effort values. Prices checked October 24, 2026; this abbreviated table excludes caching, long-context adjustments, special tiers, and tools. The actual accounting must use complete provider billing categories and dated rates. Catalog support does not prove account access, successful Codex execution, or task reliability.

Use standard processing and ordinary reasoning mode initially. Do not add expensive tiers or a third flagship without a specific development result justifying its scientific value. Pin immutable model versions if available; otherwise log aliases, returned identifiers, dates, and any provider changes.

The pilot must establish which combinations solve different tasks. If one configuration dominates, do not invent difficulty labels to manufacture a routing advantage.

## Benchmark recommendation

Keep SWE-bench central. Use a small pinned development subset to verify execution, then choose a defensible final dataset and sampling policy before collecting training labels.

[SWE-bench Pro V2's dated September 22 update](https://labs.scale.com/leaderboard/swe_bench_pro_public_v2) describes 642 tasks across 11 repositories, corrected instructions, restricted networking, and pristine regrading. Its page also contains older dataset descriptions. Name the exact version, task IDs, language/repository coverage, and evaluator; do not mix V1 and V2 claims.

A modest SWE-bench Verified subset remains a possible plumbing pilot. It should not automatically become the paper's sole benchmark. Neither publicly available benchmark is established here as contamination-free. Training on one collection and testing on another introduces domain shift that needs its own interpretation.

A standard issue-to-patch SWE-bench run has one initial user request. It can measure initial configuration selection, but cannot establish gains from rerouting between user messages. The separate controlled multi-turn evaluation is necessary for that claim.

## Financial interpretation

The owner reports $3,333 in OpenAI API credits. This supersedes the earlier $3,000 estimate; balance, expiry, eligible models, and account access have not been independently verified. These credits are a resource ceiling, not an experiment allocation.

[OpenAI subscription pricing](https://learn.chatgpt.com/docs/pricing) distinguishes included Codex usage from API billing. Use included development tooling and offline checks where practical. [Hosted Jev](https://openrouter.ai/docs/guides/community/jev) bills through its own provider path. GPU training, hosting, and benchmark compute require a separate funding plan.

For the paper, record resource consumption even if credits cover the bill. Distinguish cash outlay, API-credit consumption, measured inference usage, and price-equivalent estimates. A subscription-backed run is not a zero-cost model result and must not be pooled silently with API-billed timing/cost measurements.

## What remains unproved

Actual account access and per-turn execution; the readable pinned OpenJev helper and exact training serialization; a compatible adapter backward pass and GPU fit; final dataset/environment feasibility; acceptable success loss; affordable sample size; and project-specific gain over simpler controls.

These gaps are tracked as decisions and later validation gates in [Development plan](development-plan.md). Do not respond to them by claiming universal optimality, starting a large experiment, or substituting a different OpenJev project.

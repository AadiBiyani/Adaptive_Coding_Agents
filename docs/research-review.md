# Research and technology review

Reviewed October 24, 2026. These are source-backed findings and design recommendations, not implementation results. The review is sufficient to improve the plan, but it is not an exhaustive novelty search or a guarantee of publication.

## Recommendation

Build a small routing layer around the Codex harness with one execution path for terminal use and benchmarks. Following the owner's clarification that there is no language requirement, the current recommendation is Python for the initial client/router and research work. Start with a restricted GPT model/effort pool and measure routing opportunity before expanding training or evaluation. Keep development independent of the inactive Milestone 2 schedule.

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

The owner selected fine-tuned versus untuned OpenJev as the primary research contrast: does task-specific training improve routing enough to increase executable task success or reduce cost/token usage? Phase 1 clarifies the mechanism: task-type/signal classification followed by a separate mapping to GPT model/effort. Hold that mapping and taxonomy fixed in the primary classifier comparison. The proposed contribution is a controlled study of that contrast, with fixed, rule-based, cheap learned, and hosted Jev controls. Later-message adaptation is secondary. Count annotation, classification, switching, data collection, and training costs when interpreting gains.

That contribution is a hypothesis to refine against the closest methods. A product integration can be useful even if the paper ends up as a careful empirical study rather than a new routing algorithm. Never label the project “first” without a much stronger literature review.

## Stack recommendation

TypeScript plus Python was a reasonable earlier candidate, but was incorrectly described as the owner's requirement. Python-first now has the stronger simplicity case for this small research product: shared routing/data logic, direct use of the cheap learned baseline, and one application language. This is a maintenance judgment, not a claim of lower model-token charges. TypeScript retains an advantage in generated app-server types and examples; adopt it only if client coverage or another concrete need outweighs the extra boundary.

| Layer | Recommendation | Reason and boundary |
| --- | --- | --- |
| Terminal client and router | Python with typed, validated records | Share policy/features with research tools and use the same execution path interactively and in benchmarks. |
| Runtime/tooling | Candidate Python 3.12, uv locks | Pin compatible versions before setup. If a TypeScript client becomes necessary, Node.js 24 LTS/npm is the candidate; [Node's release table](https://nodejs.org/en/about/previous-releases) distinguishes it from the locally observed Node 26. |
| Codex integration | Version-pinned app-server via stdio; lower-level typed Python client with explicit approval handling | The [official app-server](https://learn.chatgpt.com/docs/app-server) provides history, approvals, and streamed events. Required client controls were inspected in official source; published package compatibility and live behavior remain to be verified. |
| Python work | Python 3.12 candidate, uv lockfiles; separate training and evaluator environments | Keep benchmark dependencies independent of GPU/CUDA serving libraries. Python patch versions and exact compatible library pins must be resolved before installation. [uv project documentation](https://docs.astral.sh/uv/concepts/projects/) describes its lock/sync workflow. |
| Training | PyTorch, Transformers, PEFT; supervised adapters first | Use reviewed category-option supervision; measured configuration outcomes inform the separate routing policy. QLoRA and GPU fit require verification. |
| Evaluation | Official task evaluator in isolated Linux containers; Python orchestration and analysis | Preserve grading semantics and invoke the same Codex execution path used by the terminal. |
| Storage and contracts | Versioned JSON Schema, JSONL records, hashed manifests; Parquet only if useful for analysis | Avoid an unnecessary database, queue service, or observability subscription in the first study. |
| Verification | Python typechecking, offline protocol checks, and pytest for important data/evaluator behavior | Routine regression checks should not need paid inference. Select dependencies when the design gate closes. |

The [Codex SDK guide](https://learn.chatgpt.com/docs/codex-sdk) documents a stable Python SDK controlling app-server with a pinned runtime. Subsequent official-source inspection covered per-turn settings, notifications, interruption, resume, and approval handling. The lower-level typed client accepts an explicit approval handler; the high-level convenience constructor does not expose that handler and its default accepts command/file-change requests. Use the explicit client surface if a compatible published package exposes it; do not modify private SDK fields. [Technical discovery](technical-discovery.md#documented-codex-interface-candidates) records source pins and remaining validation. Python-first replaces the proposed TypeScript client rather than adding a second one.

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

Phase 0 selected a small pinned SWE-bench Verified development subset for the first pipeline pilot, excluding its tasks and related derivatives from held-out use. It should not automatically become the paper's sole benchmark. Neither publicly available benchmark is established here as contamination-free. Training on one collection and testing on another introduces domain shift that needs its own interpretation. Fix final cohort/version and sampling rules before collecting labels.

A standard issue-to-patch SWE-bench run has one initial user request. It can measure initial configuration selection, but cannot establish gains from rerouting between user messages. The separate controlled multi-turn evaluation is necessary for that claim.

## Financial interpretation

The owner reports $3,333 in OpenAI API credits. This supersedes the earlier $3,000 estimate; balance, expiry, eligible models, and account access have not been independently verified. These credits are a resource ceiling, not an experiment allocation. The owner will select the initial API cap after reviewing a run-by-run estimate. Cloud spending must remain strictly under $50 cumulatively; conservatively include other non-OpenAI cash costs until separately reviewed. The [Phase 0 record](phase-0-decisions.md#cloud-shortlist-and-funding-process) compares Modal and Runpod as candidates without assuming included-credit eligibility or training fit.

[OpenAI subscription pricing](https://learn.chatgpt.com/docs/pricing) distinguishes included Codex usage from API billing. Use included development tooling and offline checks where practical. [Hosted Jev](https://openrouter.ai/docs/guides/community/jev) bills through its own provider path. GPU training, hosting, and benchmark compute require a separate funding plan.

For the paper, record resource consumption even if credits cover the bill. Distinguish cash outlay, API-credit consumption, measured inference usage, and price-equivalent estimates. A subscription-backed run is not a zero-cost model result and must not be pooled silently with API-billed timing/cost measurements.

## What remains unproved

Actual account access and per-turn execution; compatible published SDK pins; exact tokenizer/loss implementation; a compatible adapter backward pass and GPU fit; final dataset/environment feasibility; acceptable success loss; affordable sample size; and project-specific gain over simpler controls. The pinned OpenJev helper has now been read and hash-verified; that resolves its source/readout inspection, not training compatibility.

These gaps are tracked as decisions and later validation gates in [Development plan](development-plan.md). Do not respond to them by claiming universal optimality, starting a large experiment, or substituting a different OpenJev project.

# Phase 0 decisions

Completed October 24, 2026 at the requirements and design-discovery level. The owner answered the scope and resource questions; source inspection resolved the integration/readout choices. This does not mean live execution, GPU fit, or research performance has been proved. Those checks have explicit later gates below. Phase 1's contracts come next; no implementation or paid experiment was started.

**Subsequent Phase 1 clarification:** The owner confirmed task-category classification followed by a separate routing policy, selected a task type plus signals, and restricted classifier task content to the current user prompt only. Automatic reliable fallback handles insufficient prompt information within remaining limits; Codex retains its session context. These decisions supersede the direct-choice/context-enriched proposals and change classifier supervision to prompt-only category annotations, with measured coding outcomes informing the policy. Additional classifier context is a later option under discussion, not an approved initial input. [Phase 1 specification](phase-1-specification.md) is the current contract review.

## Confirmed owner decisions

| Topic | Answer and consequence |
| --- | --- |
| Language preference | No TypeScript requirement. That was an earlier agent recommendation; choose the stack on technical merit and maintenance cost. |
| First intended use | Research and personal testing first. Commercial/workplace deployment is a later decision. |
| First task domain | Python repositories for training and benchmarking. This is independent of the router's implementation language. |
| Primary research question | Does fine-tuning OpenJev improve routing versus untuned OpenJev, leading to better task performance or lower price/token usage? |
| Existing compute | The owner believes a Linux server is available. Access, hardware, container support, and quotas are unverified. No free GPU allocation is confirmed; paid Purdue RCAC access was mentioned. |
| Cloud spending | Willing to spend on Modal or another suitable GPU provider, strictly under $50. Treat this as a cumulative cloud ceiling, not a per-job allowance. Conservatively plan all non-OpenAI cash costs inside it until separately reviewed. |
| OpenAI credits | Owner reports $3,333; preserve them. Decide the initial spending cap only after reviewing a run-by-run estimate. Neither the proposed $10 nor $25 cap was selected. |
| Existing scope | Terminal workflow, routing at new user prompts, GPT model plus effort, debugging, OpenJev fine-tuning, SWE-bench, multi-turn evaluation, and correctness-first priorities remain. |

## Selected design direction

**Stack:** Python for the initial terminal/router, data, training, benchmark orchestration, and analysis. This is an engineering choice supported by a common language for policy/features and research tools; it is not a newly asserted owner preference. Use candidate Python 3.12 with uv and separate runtime, training/serving, and evaluator dependency environments. Pin exact packages in Phase 1. TypeScript remains an alternative if a demonstrated limitation warrants it; no second client is planned.

**Harness integration:** One Python client driving version-pinned Codex app-server over stdio for both interactive and benchmark execution. Target the inspected 0.164.0 interface initially. Reuse the SDK's lower-level typed client with an explicit approval handler if the published package exposes the inspected surface; do not monkey-patch the high-level convenience client. If that surface is unavailable in a compatible distribution, review a narrow protocol adapter before implementation.

The [official SDK guide](https://learn.chatgpt.com/docs/codex-sdk) establishes the Python/app-server path. Official source inspection at [Codex revision 970111f6cb62cc02fe36a82ea7d71b37a2889c97](https://github.com/openai/codex/tree/970111f6cb62cc02fe36a82ea7d71b37a2889c97/sdk/python) covered the API reference and clients; approval handling was also checked at tag `rust-v0.164.0`. The [typed client](https://github.com/openai/codex/blob/rust-v0.164.0/sdk/python/src/openai_codex/client.py) provides an `approval_handler` constructor argument, thread/turn operations, interruption, notifications, and generic requests. Its default accepts command/file-change approval requests; our integration must supply explicit handling. The high-level `Codex(...)` constructor does not expose that handler in the inspected source. These are source findings, not live test results.

**Classifier contract at Phase 0, now superseded:** One typed configuration choice was proposed. Phase 1 instead confirms task-type/signal classification followed by a separate mapping to model/effort. Initial model candidates remain `gpt-6-luna` and `gpt-6.1-sol` at low/high, pending actual account and execution validation. Routing happens before new user prompts; internal steps do not reroute. Exact state bounds and fallback parameters belong to Phase 1.

**Training direction:** Adapt the independent `openjev/openjev` 27B checkpoint with supervised LoRA and preserve its option-token readout. Phase 1 refines the target to reviewed category-option labels; measured executable outcomes inform the separate policy. QLoRA is conditional on compatibility; no reinforcement-learning or full-parameter training is planned initially. Use the same parent, permitted inputs, precision, and serving/calibration conditions for untuned/tuned comparisons, with a shared fixed mapping. GPU fit and the actual recipe require a capped compatibility job, not a promise from documentation.

**Readout inspection:** The pinned [helper source](https://huggingface.co/openjev/openjev/blob/b4a89f5884f3482a5e894b2e7ff01db8ea033726/helper/shim.py) was downloaded for reading only after sandbox network permission was granted. Its SHA-256 is `81a22f1b1b8912a465059207ef9f60b7c6c16b4de6372305d867efbe38a1987a`, matching the serving document. The text path serializes state, question, and letter-labelled options; targeted first-output scoring supplies a choice per question. Use plain-string instructions, pinned ordering, and the exact tokenizer/chat template; Phase 1 sets the category questions and counts their separate work. No helper or model code was executed. Details and remaining training checks are in [Training plan](training-plan.md).

**Benchmark direction:** Start with a small development/pipeline subset of SWE-bench Verified and controlled Python multi-turn scenarios. Exclude all pilot tasks and related derivatives from final held-out use. Final training/development/held-out manifests and the choice of a broader paper cohort, including whether Pro V2 adds affordable value, must be fixed in Phase 1 before label collection. A subset result is not a full official leaderboard score. Use the same executable coding path for all strategies.

**Execution environment:** Local machine for planning and offline development; isolated Linux containers for benchmark repository execution and clean patch grading; cloud GPU for OpenJev compatibility/training/temporary serving. Prefer the existing Linux server for CPU evaluation if its access, resources, and container support are confirmed. Otherwise price an isolated cloud alternative within the cash ceiling. Do not assume the Apple Silicon laptop or an unverified server can run the selected images unchanged.

**Research priorities:** The primary matched contrast is tuned versus untuned OpenJev on executable task outcomes and cost. Strong fixed, rules, cheap learned, and hosted Jev arms remain controls. Multi-turn adaptation is secondary; expand its ablations only when claiming an adaptation benefit. Task success and dollars are the principal outcome pair; token usage is also reported, since fewer tokens across different models need not mean a lower bill.

## Cloud shortlist and funding process

[Modal pricing](https://modal.com/pricing), checked October 24, lists $30/month of included Starter compute, an A100 80 GB base rate of about $2.50/hour, and H100 SXM about $3.95/hour, before CPU, host memory, and applicable additional charges. Eligibility and remaining included usage are unverified. [Runpod pricing](https://www.runpod.io/pricing) lists A100 80 GB Pod options at $1.79/hour and H100 PCIe at $2.89/hour; live availability, storage, throughput, and setup time also matter.

Use Modal as the first candidate to assess because included compute could reduce cash spending; retain Runpod as a comparison for the actual job. Neither is established as cheapest for this checkpoint. No account, deployment, subscription, or job was created. Do not count unverified free credits or promise a full study fits under $50.

Before any paid stage, prepare its exact runs, purpose, token limits, current rates, expected and conservative cost, retry policy, maximum duration, and stop condition. The owner chose to review that estimate before setting the API cap. Include all attempts and separate API-credit use from cash. Cash estimates must respect the under-$50 cumulative cloud constraint, with room for storage and failures.

## Validation gates carried into later phases

| Unknown | When and how to resolve | Stop condition |
| --- | --- | --- |
| Published Python package/runtime and exact interface | Phase 1: check distribution pins and reviewed API/source; Phase 2: offline protocol fixtures and bounded live continuity/setting proof. | No automatic approvals, missing control silently ignored, or unsupported interface accepted as working. |
| Actual GPT access/billing/settings | Before the first estimated live batch, inspect through an authorized path and record observed settings/usage. | Do not retry the previously declined account-inspection escalation without renewed authorization; do not run an unapproved API batch. |
| Tokenizer/readout and adapter compatibility | Phase 1 specifies the serializer/loss; Phase 6 checks tokenizer IDs, finite gradients, frozen base, adapter updates, memory, save/reload, and option scores. | Stop on incompatibility or cap exhaustion; review a changed recipe rather than automatically renting more hardware. |
| Linux/container availability | Before evaluator implementation depends on it: check host access/resources, permitted container runtime, images, and clean grading fixtures. | Do not execute benchmark repositories directly on the developer's host or treat environment failure as model failure. |
| Useful routing signal and affordable sample | Phase 3 fixed pilot, then variance/cost-informed collection and final-evaluation estimates. | Narrow paid expansion and claims if headroom or affordable precision is insufficient; do not silently drop fine-tuning. |

## Phase 1 handoff

Specify the user interaction, exact context inputs/truncation, configuration/fallback rules, timeouts/retries/budget behavior, event/accounting contracts, data splits, multi-turn controller, outcome labels, and reliability analysis. Those are the next questions/design tasks. Completing Phase 0 does not authorize starting the prototype or paid runs.

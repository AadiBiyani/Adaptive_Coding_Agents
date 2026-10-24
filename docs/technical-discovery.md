# Technical discovery for implementation planning

Updated October 24, 2026. This record distinguishes local inspection, documentation, failed attempts, and unverified live behavior. The earlier premature prototype and generated schema files were deleted at the owner's request. No successful model call, benchmark execution, or training job has been established.

## Local Codex evidence

`codex --version` reported `codex-cli 0.164.0`; the local Node version observed earlier was 26.3.1. The recommended project runtime is Node.js 24 LTS, not an accidental dependency on the globally installed version. Exact installation/pinning remains future work.

`codex app-server --help` lists the experimental app-server, stdio transport, and `generate-ts` / `generate-json-schema`. Before the reset, schemas were generated under `build/codex-schema/` and inspected. They included thread continuity, per-turn model/effort, paginated model discovery, approval, cancellation, and token-usage records. Those generated artifacts are now deleted; regenerate from the chosen pinned CLI when implementation begins.

The previous prototype's offline tests and simulated demo ran, but they did not prove real model execution. An attempted read-only account/model inspection failed because app-server could not initialize local SQLite state under `~/.codex` within the filesystem restrictions. The escalation was declined. Do not retry it or bypass that denial without renewed authorization. No account access, credit eligibility, or live capability list was obtained.

## Documented Codex interface candidates

The [official app-server documentation](https://learn.chatgpt.com/docs/app-server) and inspected local schemas support the following integration surface; implementation must use exact version-matched fields and enums:

| Need | Interface |
| --- | --- |
| Initialize | `initialize`, then `initialized`. |
| Conversation continuity | `thread/start`, `thread/resume`. |
| Configured new user turn | `turn/start`: `threadId`, `input`, `model`, `effort`. |
| Capability discovery | `model/list`, `supportedReasoningEfforts`, pagination via `nextCursor`. |
| Progress/completion | Streamed item events, including `item/agentMessage/delta`, and `turn/completed`. |
| Approvals | Command execution, file change, and permission request methods. |
| Usage | `thread/tokenUsage/updated`; local records include cumulative and recent totals, not a guaranteed itemized bill. |
| Cancellation | `turn/interrupt`. |

The documentation's “Getting started,” “Start or resume a thread,” “Start a turn,” “List models,” and “Approvals” sections are the implementation reference points. Some website examples differ from the installed schema's enums; copy patterns only after matching versions.

New-turn overrides can affect session defaults, so send explicit registry settings for every turn. `turn/steer` does not accept a model/effort override. Queue new prompts until the active turn completes, or use a separate explicit cancellation. Model changes can introduce switch instructions and context/cache overhead; include those effects in the experimental record.

The [SDK guide](https://learn.chatgpt.com/docs/codex-sdk) distinguishes custom interactive clients from automation. A TypeScript app-server client shared by terminal and benchmarks is the recommendation, not evidence that a stock-terminal router hook exists.

Still unverified: live session/resume/tool behavior, supported settings actually executed, model access, billing path, provider rerouting visibility, and sufficiently detailed call/retry accounting. Aggregate usage cannot establish every internal call or exact billed dollars. Do not mark those questions resolved from a schema alone.

## Classifier dependencies

The [OpenRouter Jev guide](https://openrouter.ai/docs/guides/community/jev) documents typed `state`/`questions` decisions, including Choice, at `/api/alpha/decisions` and `/api/v1/systemone`. That provider path is separate from direct OpenAI API credits. Select the exact supported endpoint/model version and failure semantics before implementation; no hosted classifier call has been made.

The [OpenJev model card](https://huggingface.co/openjev/openjev) describes an independent 27B checkpoint with option-token readout and a helper endpoint. It is not established as hosted TypeSafe Jev's released weights. The serving documentation gives a pinned GPU inference recipe, not proof of adapter training compatibility or memory fit.

The review established a checkpoint/configuration candidate, but the exact helper source still needs inspection. [Training plan](training-plan.md) records the sources, remaining serialization questions, LoRA/QLoRA compatibility gate, and matched untuned/tuned conditions. Do not equate a GPU serving result with a fine-tuning feasibility result.

## Benchmark dependency

The [SWE-bench evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/) describes containerized patch evaluation and prediction records containing `instance_id`, `model_name_or_path`, and `model_patch`. The [installation guide](https://www.swebench.com/SWE-bench/installation/) lists Python/Docker prerequisites. Use unique run identifiers and clean grading; execution completion does not imply resolution.

The final variant, cohort, evaluator revision, CPU architecture, image availability, disk/memory needs, and isolated agent execution environment remain to be selected. Pro V2 is a candidate documented in [Research review](research-review.md), not a dataset already installed or adopted. Do not assume an evaluator command for one variant applies unchanged to another. No benchmark repository code was executed on the developer's host.

## Planning consequences

The TypeScript/Python division is now confirmed. Recommended models, training method, and evaluator choices have explicit sources and validation gates. Finish the design contract before implementing the shared session client, then prove measurement and fixed baselines before expensive label collection or training. Follow [Development plan](development-plan.md); the course schedule is inactive.

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

The [SDK guide](https://learn.chatgpt.com/docs/codex-sdk) documents a stable Python app-server client with a pinned runtime. Following the owner's language clarification and the source inspection below, Python-first is the selected design direction. The previously proposed TypeScript client is an alternative, not a required second implementation or proof of a stock-terminal router hook.

The subsequent official source review covered the [Python API reference](https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/sdk/python/docs/api-reference.md), `api.py`, and synchronous/asynchronous clients at revision `970111f6cb62cc02fe36a82ea7d71b37a2889c97`. It confirms per-turn model/effort, streamed handles, interruption, resume, and usage. The lower-level [CodexClient at rust-v0.164.0](https://github.com/openai/codex/blob/rust-v0.164.0/sdk/python/src/openai_codex/client.py) accepts an `approval_handler`; its default accepts command/file-change approvals. The high-level constructor does not expose that callback. Prefer a thin wrapper over the pinned lower-level client with explicit handling, not private-field modification or default approval behavior.

The approval callback runs on the transport reader thread; its design must avoid synchronously issuing an RPC that waits for that same reader. Model discovery's convenience method does not expose pagination, so use the supported generic request path with the version-matched schema when more pages exist. These are source-level integration constraints, not live validation. Verify the published distribution before depending on a module surface outside the curated high-level API.

Still unverified: live session/resume/tool behavior, supported settings actually executed, model access, billing path, provider rerouting visibility, and sufficiently detailed call/retry accounting. Aggregate usage cannot establish every internal call or exact billed dollars. Do not mark those questions resolved from a schema alone.

## Classifier dependencies

The [OpenRouter Jev guide](https://openrouter.ai/docs/guides/community/jev) documents typed `state`/`questions` decisions, including Choice, at `/api/alpha/decisions` and `/api/v1/systemone`. That provider path is separate from direct OpenAI API credits. Select the exact supported endpoint/model version and failure semantics before implementation; no hosted classifier call has been made.

Phase 1 uses those questions for task categories and signals, with model/effort chosen by a separate policy. The [OpenJev model card](https://huggingface.co/openjev/openjev), rechecked for this clarification, describes multiple questions in one request but one forward pass per question. A multi-field classification therefore needs per-question work/accounting. Both hosted and independent model interfaces support the proposed typed-category pattern; source support does not establish project classification quality or downstream savings.

The [OpenJev model card](https://huggingface.co/openjev/openjev) describes an independent 27B checkpoint with option-token readout and a helper endpoint. It is not established as hosted TypeSafe Jev's released weights. The serving documentation gives a pinned GPU inference recipe, not proof of adapter training compatibility or memory fit.

The exact pinned helper was subsequently retrieved after sandbox network permission was granted, read, and matched to its published SHA-256. Its text serialization and targeted option-token readout are now documented in [Training plan](training-plan.md). The tokenizer/loss implementation, LoRA/QLoRA backward-pass compatibility, memory, and save/reload behavior still require later checks. The helper was not executed; a serving result does not prove training feasibility.

## Benchmark dependency

The [SWE-bench evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/) describes containerized patch evaluation and prediction records containing `instance_id`, `model_name_or_path`, and `model_patch`. The [installation guide](https://www.swebench.com/SWE-bench/installation/) lists Python/Docker prerequisites. Use unique run identifiers and clean grading; execution completion does not imply resolution.

The final variant, cohort, evaluator revision, CPU architecture, image availability, disk/memory needs, and isolated agent execution environment remain to be selected. Pro V2 is a candidate documented in [Research review](research-review.md), not a dataset already installed or adopted. Do not assume an evaluator command for one variant applies unchanged to another. No benchmark repository code was executed on the developer's host.

## Planning consequences

Phase 0 discovery is complete at the design level. Python-first, research/personal testing, Python task repositories, a Verified development pilot, the fine-tuned-versus-untuned primary question, an under-$50 cloud ceiling, and estimate-first API spending are recorded in [Phase 0 decisions](phase-0-decisions.md). Live validation remains scheduled. Complete Phase 1's contracts before implementing the client, then prove measurement and fixed baselines before expensive collection or training. The course schedule remains inactive.

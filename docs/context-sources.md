# Context sources and boundaries

## Established project context

The initial development documents carry forward the owner's project-planning conversation and the finalized Milestone 1 `brief.md`. The proposal and exact submission ZIP were finalized on September 28, 2026. The original brief was confirmed by the owner as the wording reviewed by the stakeholder. The private submission records establish the administrative context; they are not benchmark evidence or proof of implementation.

`docs/project-brief.md` is a development adaptation that omits personal stakeholder details and student identifiers. It is not a replacement for the exact reviewed source brief and must not be represented as new stakeholder approval.

The architecture, record layouts, and ordered development steps expand the agreed research scope into proposed implementation work. They do not establish that a particular API, cloud platform, training recipe, or result has already been verified.

## Additional conversation

The owner requested context from [another project conversation](https://chatgpt.com/g/g-p-6ab4b0833f0481919c3407d492196d3c-ece-570/c/6ab59de5-1af0-83ea-9f33-2a60be7daabf). The automated web reader could not load it, and no browser connection was available. On October 19, 2026, the owner pasted the relevant proposal into the current conversation. That supplied text is incorporated in [Research hypotheses and extensions](research-notes.md) and the architecture/evaluation plans. The private URL itself was not read.

The pasted material is the original broader research proposal, also discussed before the later Milestone 1 decisions. It proposes task-progress signals, joint model/effort selection, direct versus policy-based routing, internal checkpoints, additional comparison arms, and related-work leads. The development documents retain those ideas while preserving the later agreed initial scope. Statements in the pasted text about current vendor APIs or prior research are leads to verify, not newly checked technical facts.

## October 24 corrections and research review

The owner reaffirmed TypeScript plus Python, corrected the reported OpenAI API-credit amount to $3,333, emphasized minimal consumption, and stated an intention to develop an ML paper. The owner then requested deletion of the premature prototype, set the Milestone 2 schedule aside, and required a coherent design before more coding. Those instructions take precedence over the historical schedule and earlier estimates.

The prototype archive, generated schemas, and empty implementation directories were deleted. Documentation was revised; no paid experiment, trained model, or benchmark result was produced by this review. Local schemas had been inspected before deletion. A prior live account/model inspection failed on a restricted Codex database write, and the escalation was declined; access was not verified and the denial must not be bypassed.

[Technical discovery](technical-discovery.md) records local observations and unverified live behavior. [Research review](research-review.md) records current primary-source findings and recommendations, including model candidates and related-work overlap. [Training plan](training-plan.md) distinguishes the readable OpenJev release/configuration/serving material from the helper inspection and backward-pass proof still needed. These reviews are not an exhaustive literature survey or a guarantee that a proposed recipe fits a GPU.

## Technical references to recheck before use

These pointers supplement the dated findings above. Interfaces, account access, prices, and requirements can change; a documentation check is not a successful integration or experiment.

- [Codex app-server documentation referenced during planning](https://learn.chatgpt.com/docs/app-server)
- [Codex hooks documentation referenced during planning](https://learn.chatgpt.com/docs/hooks)
- [OpenJev model card](https://huggingface.co/openjev/openjev)
- [Hosted Jev documentation](https://openrouter.ai/docs/guides/community/jev)
- [SWE-bench evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/)
- [SWE-bench benchmark and leaderboards](https://www.swebench.com/)

Inspect installed Codex capabilities and current official documentation before implementing against these references. In particular, verify the supported per-turn model/effort mechanism, the exact OpenJev checkpoint/training requirements, classifier access and pricing, and benchmark execution support for the chosen compute environment.

## Material intentionally kept elsewhere

The private course workspace retains student/contact records, stakeholder agreement versions, approval email/image/PDF, consent audio, exact stakeholder-facing brief PDF, and the final submission ZIP. These are not needed to run or understand the development repository and are not copied here. No access to a former employer's internal code, datasets, or benchmarks is assumed.

Future raw traces, patches, task data, model weights, and private feedback should use appropriate local or artifact storage with references and hashes in reviewed experiment records. Source URLs alone do not grant permission to redistribute their contents or commit proprietary data.

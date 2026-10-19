# Context sources and boundaries

## Established project context

The initial development documents carry forward the owner's project-planning conversation and the finalized Milestone 1 `brief.md`. The proposal and exact submission ZIP were finalized on September 28, 2026. The original brief was confirmed by the owner as the wording reviewed by the stakeholder. The private submission records establish the administrative context; they are not benchmark evidence or proof of implementation.

`docs/project-brief.md` is a development adaptation that omits personal stakeholder details and student identifiers. It is not a replacement for the exact reviewed source brief and must not be represented as new stakeholder approval.

The architecture, record layouts, and ordered development steps expand the agreed research scope into proposed implementation work. They do not establish that a particular API, cloud platform, training recipe, or result has already been verified.

## Additional conversation

The owner requested context from [another project conversation](https://chatgpt.com/g/g-p-6ab4b0833f0481919c3407d492196d3c-ece-570/c/6ab59de5-1af0-83ea-9f33-2a60be7daabf). The automated web reader could not load it, and no browser connection was available. On October 19, 2026, the owner pasted the relevant proposal into the current conversation. That supplied text is incorporated in [Research hypotheses and extensions](research-notes.md) and the architecture/evaluation plans. The private URL itself was not read.

The pasted material is the original broader research proposal, also discussed before the later Milestone 1 decisions. It proposes task-progress signals, joint model/effort selection, direct versus policy-based routing, internal checkpoints, additional comparison arms, and related-work leads. The development documents retain those ideas while preserving the later agreed initial scope. Statements in the pasted text about current vendor APIs or prior research are leads to verify, not newly checked technical facts.

## Technical references to verify during implementation

These are reference pointers from planning, not a statement that current APIs, prices, supported models, or hardware requirements have been revalidated during repository setup.

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

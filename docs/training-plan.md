# OpenJev training plan

Reviewed October 24, 2026. Fine-tuning remains a project deliverable. This document specifies a proposed, gated method; no training dataset, GPU job, tuned checkpoint, or verified memory requirement exists yet.

## Model identity and readout

Use the independent [openjev/openjev checkpoint](https://huggingface.co/openjev/openjev), not an assumed release of hosted TypeSafe Jev weights. The model card describes a 27B model and labels its weights CC BY-NC 4.0. The helper code has a separate license. Check the exact license files and intended use before distributing artifacts or deploying in a workplace; course research does not itself establish permission for every later use.

The reviewed release candidate is [revision b4a89f5884f3482a5e894b2e7ff01db8ea033726](https://huggingface.co/openjev/openjev/commit/b4a89f5884f3482a5e894b2e7ff01db8ea033726). Its [NOTICE](https://huggingface.co/openjev/openjev/raw/main/NOTICE) identifies `Qwen/Qwen3.8-27B` as the upstream base. The reviewed [configuration](https://huggingface.co/openjev/openjev/blob/main/config.json) names `Qwen3_5ForConditionalGeneration`, `model_type: qwen3_5`, BF16, and `language_model_only: false`. Pin the actual files and module structure; do not infer the correct training class from the repository name alone.

The [serving instructions](https://huggingface.co/openjev/openjev/raw/main/serve/SERVE.md) describe first-output-position option scoring, a `/v1/systemone` helper, targeted option-token readout, calibration settings, and `/v1/version` provenance. The request's model name is not sufficient proof of the checkpoint loaded by a single-model helper. Record the server's actual version/checkpoint information.

The reviewed serving environment pins vLLM 0.29.0, PyTorch 2.13.0+cu130, Transformers 5.17.0, and PEFT 0.21.0. Those are serving references, not a validated training dependency set. The published H100 80 GB FP8 serving recipe establishes neither backward-pass support nor training fit. No end-to-end fine-tuning recipe or project-ready labeled training set was established in the reviewed release material.

**Open design dependency:** Read the exact pinned helper implementation and tokenizer before writing the serializer or loss. The model card and serving instructions were readable; the helper source fetch did not succeed in this review. Confirm the prompt template, option-to-token mapping, first-output index, masking, and calibration rather than recreating them from assumptions.

## Outcome data and labels

1. Freeze train/development/held-out groups before generating examples. Keep related issues, derived scenarios, all turns of a task, and near duplicates together. A repository holdout can test transfer if enough repositories remain for a useful study; task grouping alone does not demonstrate repository generalization.
2. Capture a routing state containing the current user prompt, bounded already-visible context, permitted progress signals, eligible configuration descriptions, and remaining limits. Store the exact context-selection version. Exclude reference patches, hidden checks, future messages, and outcomes being predicted.
3. Execute candidate GPT configurations from comparable states and obtain executable success, complete inference cost, and latency. Reuse valid fixed-pilot records from eligible splits. Label collection can cost more than adapter training; budget it explicitly.
4. Prefer configurations with sufficiently supported successful outcomes under the reviewed reliability rule, then compare cost/time. Choose the numerical tolerance and uncertainty treatment on development data. Preserve multiple acceptable choices or abstain from ambiguous labels rather than converting every noisy observation into a hard winner.
5. Keep all-candidates-failed states as failure evidence. They can inform a documented fallback policy, but must not be labeled as successful cheap routes. A single attempt is an observed outcome, not an estimate of universal success probability.
6. Collect later-turn examples only when the exact pre-decision repository and valid conversation state can be reconstructed for alternative configurations. If this is infeasible, begin with initial-prompt training and explicitly test/disclose its transfer to later prompts.

Each label must reference the runs that support it, the label-rule version, and any uncertainty or exclusion reason. Use the same training evidence for the cheap learned baseline and OpenJev adaptation. Audit option balance and ordering; prevent a fixed position from becoming a shortcut for the target model.

## Proposed training loop

Use supervised adapter training first. LoRA updates a small set of added parameters while keeping base weights frozen. Four-bit QLoRA may reduce memory use, but it is a conditional optimization: exact model support, kernels, gradients, and save/reload behavior need proof. Full-parameter fine-tuning and reinforcement learning are not the initial cost-conscious choices.

Serialize each permitted state and eligible-choice question using the pinned OpenJev convention. Supervise the selected option at the verified readout position; mask context tokens from the objective. For tied acceptable choices, select and document a consistent target rule or validated soft-label objective before collecting the final dataset. Avoid teaching long generated rationales that the product does not require.

The [Transformers Qwen3.5 documentation](https://huggingface.co/docs/transformers/model_doc/qwen3_5#transformers.Qwen3_5ForConditionalGeneration) documents a `labels` loss interface with ignored positions. The [PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization) describes `prepare_model_for_kbit_training`, `LoraConfig`, and `get_peft_model`; its examples are patterns to verify, not proof that OpenJev works unchanged. Inspect target module names following [PEFT custom-model guidance](https://huggingface.co/docs/peft/developer_guides/custom_models). Do not adapt a vision component merely because the configuration supports one.

Before a real job, fix the objective, adapter targets/rank, precision, sequence limit, batch/accumulation, optimizer, learning-rate schedule, seed, maximum steps, validation interval, early stopping, and checkpoint selection rule. Pick a small predeclared search using affordable development evidence. Do not run an open-ended hyperparameter sweep.

Selection should consider downstream development routing quality as well as option loss. Classification accuracy against noisy winner labels is a diagnostic, not the final coding metric. Use the same development-only calibration procedure for untuned and tuned models, and separate gains due to calibration from gains due to changed weights.

## Compatibility and memory gate

Before renting a long-running GPU, make a conservative memory estimate from the actual checkpoint, trainable modules, sequence length, batch, precision, activations, optimizer state, and runtime overhead. Compare providers by expected completed-job cost and availability. An hourly price alone cannot identify the cheapest successful training run.

The first authorized cloud job is a capped compatibility check. It must demonstrate:

- The pinned checkpoint/tokenizer load and produce valid option scores using the intended serialization.
- A tiny batch has finite loss and gradients; base parameters remain frozen and adapter parameters change after an optimizer step.
- Peak allocated/reserved GPU memory and time per step are recorded under the intended sequence limit.
- The adapter saves, reloads onto the same base, and preserves the option readout through the intended inference path.
- Stop/shutdown behavior and storage/export paths work within the job cap.

If a check fails, record the exact incompatibility and revise the recipe. A larger GPU, a different checkpoint, or a full fine-tune is a new decision with a new estimate, not an automatic retry. No particular GPU or provider is currently selected as cheapest or guaranteed to fit.

## Matched untuned and tuned comparison

Use the same parent checkpoint, tokenizer, input template, eligible choices, context limit, precision, hardware class, runtime, calibration procedure, and coding configuration pool. If a runtime cannot serve the adapted model equivalently, resolve the integration or report a separate confounded experiment; do not attribute every difference to training.

Hosted Jev has its own model and infrastructure. It is a useful system comparison, not a matched-weight ablation. Record observed latency, errors, version disclosure limits, and billed classifier usage separately.

Batch inference for experiments and stop idle endpoints. Report warm request latency and cold/startup costs distinctly; include the hosting time actually paid. Count failed jobs and checkpoint-selection attempts in development costs. Never evaluate dynamic routing by replaying a handpicked sequence of unrelated successful coding steps.

## Reproducibility and cost gate

Save dataset/split hashes, label construction, model/tokenizer/helper revisions, adapter settings, environment locks, seeds, hardware, duration, peak memory, checkpoints, validation metrics, and all charged training/hosting costs. Keep large weights and private traces out of Git; commit permitted manifests and retrieval instructions.

Before full training, compare expected adaptation cost with plausible inference savings from the development pilot. An illustrative break-even calculation is total incremental collection/training/deployment cost divided by measured savings per future task, only when those savings are positive under the required reliability criterion. Report assumptions and utilization; API credits consumed still have an economic cost even if cash payment is zero.

Freeze the selected checkpoint and policy before held-out evaluation. A neutral or negative result can answer the research question. Fine-tuning completion, improved option loss, and improved coding outcomes are three separate claims requiring separate evidence.

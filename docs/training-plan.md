# OpenJev training plan

Reviewed October 24, 2026 and updated for the owner's Phase 1 clarification: OpenJev predicts task categories/signals, while a separate policy selects the GPT configuration. Fine-tuning remains a project deliverable. This document specifies a proposed, gated method; no training dataset, GPU job, tuned checkpoint, or verified memory requirement exists yet.

## Model identity and readout

Use the independent [openjev/openjev checkpoint](https://huggingface.co/openjev/openjev), not an assumed release of hosted TypeSafe Jev weights. The model card describes a 27B model and labels its weights CC BY-NC 4.0. The helper code has a separate license. Check the exact license files and intended use before distributing artifacts or deploying in a workplace; course research does not itself establish permission for every later use.

The reviewed release candidate is [revision b4a89f5884f3482a5e894b2e7ff01db8ea033726](https://huggingface.co/openjev/openjev/commit/b4a89f5884f3482a5e894b2e7ff01db8ea033726). Its [NOTICE](https://huggingface.co/openjev/openjev/raw/main/NOTICE) identifies `Qwen/Qwen3.8-27B` as the upstream base. The reviewed [configuration](https://huggingface.co/openjev/openjev/blob/main/config.json) names `Qwen3_5ForConditionalGeneration`, `model_type: qwen3_5`, BF16, and `language_model_only: false`. Pin the actual files and module structure; do not infer the correct training class from the repository name alone.

The [serving instructions](https://huggingface.co/openjev/openjev/raw/main/serve/SERVE.md) describe first-output-position option scoring, a `/v1/systemone` helper, targeted option-token readout, calibration settings, and `/v1/version` provenance. The request's model name is not sufficient proof of the checkpoint loaded by a single-model helper. Record the server's actual version/checkpoint information.

The reviewed serving environment pins vLLM 0.29.0, PyTorch 2.13.0+cu130, Transformers 5.17.0, and PEFT 0.21.0. Those are serving references, not a validated training dependency set. The published H100 80 GB FP8 serving recipe establishes neither backward-pass support nor training fit. No end-to-end fine-tuning recipe or project-ready labeled training set was established in the reviewed release material.

**Source inspection completed:** The pinned [helper](https://huggingface.co/openjev/openjev/blob/b4a89f5884f3482a5e894b2e7ff01db8ea033726/helper/shim.py) was downloaded for reading only after sandbox network permission was granted. Its SHA-256, `81a22f1b1b8912a465059207ef9f60b7c6c16b4de6372305d867efbe38a1987a`, matches the serving document. The 26,080-byte file was inspected, not imported or executed. Tokenizer behavior, a training backward pass, and GPU fit remain to be validated.

For the text path, the helper serializes the state, question, and ordered letter-labelled choices, then uses the checkpoint's chat template with thinking disabled. Targeted readout scores the exact candidate letter IDs at the first answer position. Missing/nonfinite scores fail the request; the winning option is selected before probability rounding. The helper's confidence is a normalized preference score, not a coding-success estimate.

Use text Choice questions with plain-string instructions for the selected task type and signals, avoiding the object-instruction serialization difference between Python representation and JSON. Phase 1 proposes a small number of categorical fields; their exact definitions remain under review. Each question requires its own readout work even if questions share a request. Keep option ordering/versioning explicit, use targeted readout, and avoid extra permutation passes initially. Confirm each selected letter is exactly one distinct token under the pinned tokenizer before implementing the loss. The helper requests one output token internally but reports zero output tokens in its response; preserve that reporting distinction and measure GPU/call cost rather than treating it as free computation.

## Outcome data and labels

Separate category supervision from routing-performance evidence. The former trains OpenJev to describe the task; the latter establishes the policy that chooses the GPT model and effort. A cheapest successful configuration is not a ground-truth task category.

1. Freeze train/development/held-out groups before generating examples. Keep related issues, derived scenarios, all turns of a task, and near duplicates together. A repository holdout can test transfer if enough repositories remain for a useful study; task grouping alone does not demonstrate repository generalization.
2. Capture only the specific current user prompt as classifier task content, alongside fixed versioned category questions/definitions. Store prompt/input hashes and the input-size policy. Exclude history, summaries, repository contents/metadata, tool results, prior failures, reference patches, hidden checks, and future messages unless the user explicitly included ordinary visible details in this current prompt. Hidden evaluator material remains forbidden even if a faulty controller inserts it. Registry/pricing/budget information belongs to the downstream policy; task IDs and execution snapshots are metadata, not classifier features.
3. Define and version task-type/signal annotations from that same prompt-only view. Proposed starting fields and a low-cost manual review process are in [Phase 1](phase-1-specification.md#two-kinds-of-training-evidence); reviewer roles, sample size, quality checks, and ambiguity handling still need decisions. Annotators must not inspect extra repository/history information or label actual repair scope from a reference patch. Use unknown where the prompt does not supply enough information.
4. Separately execute candidate GPT configurations from comparable states to obtain executable success, complete cost, and latency. Reuse valid fixed-pilot records from eligible splits. These outcomes inform a common category-to-configuration mapping. Prefer sufficiently supported reliable configurations, then compare cost/time; preserve uncertainty and sparse category combinations rather than forcing a noisy winner.
5. Keep all-candidates-failed states as failure evidence for policy analysis. They must not become successful cheap-route targets. Their decision-time category annotations may still be valid. A single attempt is an observed outcome, not a universal success probability.
6. Collect later-turn classification examples from the exact user prompt for each turn, without concatenating earlier messages. Comparing alternative configuration outcomes still requires reconstructing the same repository and valid Codex conversation state, kept outside classifier features. If that is infeasible, begin with initial-state policy evidence and explicitly disclose/test transfer to later prompts.

Category labels must reference the current prompt, taxonomy and annotation procedure, reviewer/provenance, and any uncertainty/exclusion. Configuration outcomes must separately reference measured runs, execution states, limits, and grading. Use the same prompt-only category training examples for the cheap learned classifier and OpenJev adaptation and the same policy evidence downstream. Audit label/option balance and ordering; prevent a fixed position from becoming a shortcut. Any paid or model-assisted annotation needs its own estimate and quality review. Fine-tuning cannot supply information absent from a prompt; measure unknown/fallback rates before paying for a larger dataset or training sweep.

## Proposed training loop

Use supervised adapter training first. LoRA updates a small set of added parameters while keeping base weights frozen. Four-bit QLoRA may reduce memory use, but it is a conditional optimization: exact model support, kernels, gradients, and save/reload behavior need proof. Full-parameter fine-tuning and reinforcement learning are not the initial cost-conscious choices.

Serialize each permitted state and category question using the pinned OpenJev convention. Supervise the annotated category option at the verified readout position, without a context-token generation objective. Prefer a candidate-restricted cross-entropy objective over the allowed category logits to match the readout; specify the exact per-field loss, weighting, and ambiguous/unknown-label rule in Phase 1 before implementation. Ordinary masked full-vocabulary token loss is a different objective and should not be silently substituted. Avoid teaching long generated rationales that the product does not require.

The [Transformers Qwen3.5 documentation](https://huggingface.co/docs/transformers/model_doc/qwen3_5#transformers.Qwen3_5ForConditionalGeneration) documents a `labels` loss interface with ignored positions. The [PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization) describes `prepare_model_for_kbit_training`, `LoraConfig`, and `get_peft_model`; its examples are patterns to verify, not proof that OpenJev works unchanged. Inspect target module names following [PEFT custom-model guidance](https://huggingface.co/docs/peft/developer_guides/custom_models). Do not adapt a vision component merely because the configuration supports one.

Before a real job, fix the objective, adapter targets/rank, precision, sequence limit, batch/accumulation, optimizer, learning-rate schedule, seed, maximum steps, validation interval, early stopping, and checkpoint selection rule. Pick a small predeclared search using affordable development evidence. Do not run an open-ended hyperparameter sweep.

Selection should consider downstream development routing quality through the same fixed mapping as well as category loss/agreement. Better category classification does not guarantee better coding outcomes. Freeze the shared mapping before final checkpoint comparison/selection, and keep all earlier taxonomy/policy exploration within recorded training/development work. Use matched calibration settings for the primary weights comparison; separately tuned calibration or mapping is a distinct system comparison and must not be attributed solely to changed classifier weights.

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

Use the same parent checkpoint, tokenizer, input template, category definitions/options, context limit, precision, hardware class, runtime, calibration settings, downstream category-to-configuration mapping, and coding configuration pool. If a runtime cannot serve the adapted model equivalently, resolve the integration or report a separate confounded experiment; do not attribute every difference to training.

Hosted Jev has its own model and infrastructure. It is a useful system comparison, not a matched-weight ablation. Record observed latency, errors, version disclosure limits, and billed classifier usage separately.

Batch inference for experiments and stop idle endpoints. Report warm request latency and cold/startup costs distinctly; include the hosting time actually paid. Count failed jobs and checkpoint-selection attempts in development costs. Never evaluate dynamic routing by replaying a handpicked sequence of unrelated successful coding steps.

## Reproducibility and cost gate

Save dataset/split hashes, taxonomy/question versions, annotation provenance, separate policy-outcome records, mapping version, model/tokenizer/helper revisions, adapter settings, environment locks, seeds, hardware, duration, peak memory, checkpoints, validation metrics, and all charged training/hosting costs. Keep large weights and private traces out of Git; commit permitted manifests and retrieval instructions.

The owner set a cumulative cloud ceiling strictly below $50 and wants the API-credit limit chosen after a run-by-run estimate. [Phase 0 decisions](phase-0-decisions.md#cloud-shortlist-and-funding-process) records Modal/Runpod candidates and unverified included-credit possibilities; no provider or GPU job has been provisioned. Keep batch training/serving and compute costs within the reviewed allowance rather than paying for an always-on endpoint.

Before full training, compare expected adaptation cost with plausible inference savings from the development pilot. An illustrative break-even calculation is total incremental collection/training/deployment cost divided by measured savings per future task, only when those savings are positive under the required reliability criterion. Report assumptions and utilization; API credits consumed still have an economic cost even if cash payment is zero.

Freeze the selected checkpoint and policy before held-out evaluation. A neutral or negative result can answer the research question. Fine-tuning completion, improved option loss, and improved coding outcomes are three separate claims requiring separate evidence.

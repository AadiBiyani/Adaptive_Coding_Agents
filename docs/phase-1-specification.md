# Phase 1 specification

Started October 24, 2026. This phase is in progress and contains requirements plus proposed contracts, not implemented behavior. The owner confirmed task type plus a few signals, classification of only the specific current user prompt, and automatic reliable fallback for insufficiently informative prompts. Exact categories will be developed using training/development examples. No application code, test cases, model calls, or paid jobs were created for this specification.

**First-build contract selected:** The owner delegated conservative defaults and said development would begin tomorrow. [First-build defaults](first-build-defaults.md) now supplies exact offline record fields, fixture taxonomy/configurations, limits, fallback, session behavior, accounting, and runtime setup direction. That independent slice is ready for the next resumed development session. Broader experiment and live-adapter gates below remain open; no coding or installation was done tonight.

## Confirmed product flow

A new user prompt goes to Jev or OpenJev as the only dynamic task input. The classifier returns task categories and signals. A separate routing policy uses that classification, measured configuration performance, supported settings, and remaining limits to select a GPT model and reasoning effort. Codex executes the turn in the continuing session and retains its normal conversation/repository context. Repeat classification at the next user prompt; internal model/tool steps do not trigger routing.

This is the owner's intended OpenRouter-like entry point. The earlier Phase 0 proposal to ask Jev directly for a configuration ID is superseded. Jev's output describes the task; the routing policy owns the configuration choice. A direct-selection comparison is only a possible later experiment.

SWE-bench remains the primary executable bug-fix evaluation. Its evaluator determines whether generated patches resolve issues; our instrumentation measures classifier/coding usage, cost, latency, retries, and compute. The primary research comparison remains fine-tuned versus untuned OpenJev. Hosted Jev, strong fixed configurations, simple rules, and a cheap learned control remain in the plan. Multi-turn evaluation remains a secondary study.

## Prompt-only input contract

The owner explicitly chose only the specific prompt submitted for that turn. The classifier request contains that prompt plus fixed, versioned category questions, label definitions, and required serialization. Those static instructions define the classification task; they must not be enriched with dynamic session information.

Do not append conversation history, summaries, repository contents/metadata, tool outputs, earlier failures, previous classifications, or inferred progress. Do not fetch referenced files/links to expand the classifier input. Code, error messages, or other information written or pasted by the user into the current prompt are part of that prompt and may be classified. Transport identifiers and evaluation metadata stay outside model-visible task content.

The policy may still use the supported-configuration registry, measured training/development performance, and remaining operational budgets. Codex keeps its own session and tools; prompt-only classification does not reset the coding conversation. Stored repository/session snapshots support execution and evaluation, not additional classifier features.

For a short follow-up such as “try again,” return unknown/insufficient evidence where appropriate. **The owner selected automatic use of a predefined reliable fallback within the remaining budget**, without asking for clarification solely to classify that prompt. Select the fallback using development evidence; its exact model/effort is not fixed yet. If no valid fallback fits remaining limits or availability, stop with an explicit budget/availability outcome. This does not suppress normal Codex tool approvals or questions needed to perform the coding task.

Keep the submitted prompt and actual classifier input auditable. The selected first-build default limits classifier prompt text to 16,384 UTF-8 bytes; oversized text skips classification and falls back while preserving the full executor prompt. Reject non-text input initially. These application limits are not provider token limits. Do not silently summarize, enrich, or truncate user content; any later change must be explicit and shared across comparison arms. Category annotations must use the same prompt-only view.

## Context as a later research option

The owner subsequently asked whether conversation history, repository context, tool results, or prior failures should be added. The recommendation is to retain the confirmed prompt-only baseline for the first study and test additional information separately if development evidence justifies it. This question has not authorized adding those inputs. Prompt-only makes the input/annotation contract simpler and limits classifier input volume, but it is not established as the best routing strategy or cheapest complete workflow.

A prompt may omit the true repair scope, and short follow-ups can depend on conversation history. Fine-tuning cannot recover missing task facts. Inspect unknown rates, fallback use, category diversity, and executable cost/success before scaling data collection or training. If missing information appears limiting, review a small context ablation at that stage rather than paying for a larger prompt-only sweep automatically.

Prior [SWE-Router research](https://arxiv.org/html/2607.00053v1) uses a partial coding trajectory to inform continuation/escalation after exploration. That provides motivation to investigate context, not proof that it repays overhead for this different per-user-prompt policy. A possible later input is a small deterministic summary of already-visible task state at a user-message boundary. Its fields, information permissions, annotation procedure, and total cost must be specified before use; avoid starting with full history or repository ingestion.

Keep input content matched between tuned and untuned OpenJev within each comparison. To isolate a context benefit, compare input variants while holding the chosen classifier and policy conditions fixed where valid; refitted policies or retrained classifiers must be disclosed as system-level changes. No context ablation, new classifier calls, or paid runs have been authorized by this planning discussion.

## Category design under review

The owner selected **task type plus a few signals**. The following three fields and their values are a starting proposal, not a frozen taxonomy or a claim that they predict the best configuration.

| Proposed field | Candidate labels | Interpretation using only the current prompt |
| --- | --- | --- |
| Task type | Diagnose; fix; validate; mixed/unclear | Diagnose seeks an explanation or cause. Fix requests corrected behavior, including investigation needed to achieve it. Validate checks an existing change. Mixed/unclear covers cases the definitions cannot reliably separate. |
| Cause evidence described | Candidate cause with supporting details; hypothesis only; unknown | Describe what the prompt supplies. Supporting details do not prove the actual cause. Use unknown when the prompt does not establish the signal; do not consult earlier messages or tests. |
| Expected change scope | Appears localized; appears to span components; unknown | Estimate only from the prompt. Do not inspect the repository, reference patch, conversation history, or later edits to label the expected scope. |

Use one typed categorical answer per field, with versioned definitions and optional option scores where available. Keep the question count small. The [hosted Jev guide](https://openrouter.ai/docs/guides/community/jev) describes typed questions, and the [OpenJev model card](https://huggingface.co/openjev/openjev) describes one forward pass per question even when several questions share a request. Three fields therefore do not imply one classifier forward pass. Measure the complete overhead and decide whether each signal earns its cost on development data.

Use the explicitly versioned `draft-0` fixture taxonomy in the offline foundation. Refine definitions, mixed/out-of-scope handling, and annotation rules before enabling real classification or collecting labels. Keep unknown/insufficient-evidence answers distinct from malformed responses and endpoint failures. Review training/development examples for coverage, ambiguity, and signal diversity. Ordinary SWE-bench tasks may share the same broad type; measure whether extra signals help. Freeze a taxonomy version before generating its labels and the final taxonomy before held-out evaluation. Changed taxonomy requires consistent artifact versioning/relabeling.

## Classifier and policy boundary

The classifier receives only the current prompt as task content, as specified above. Task labels should be independent of model names and prices, so the classifier payload excludes the GPT registry and provider pricing. The policy receives the classification plus registry availability, remaining limits, and development-derived performance estimates. First-build size/error defaults are now specified separately; additional task-context sources remain excluded.

Each classification record must preserve taxonomy/question versions, input hash, predicted labels, available scores, classifier identity, per-question work, latency, and usage/cost provenance. Each policy record must separately preserve its mapping version, the classifications consumed, eligible configurations, selected model/effort, and any fallback reason. Missing usage remains unknown rather than zero.

Start with a transparent deterministic mapping whose entries are informed by measured development outcomes. Do not declare, for example, that a particular category always needs high effort before measuring it. Automatic reliable fallback is confirmed for insufficient prompt information; extend its exact rules to sparse categories, invalid outputs, and endpoint failures before implementation. Its selected configuration and thresholds remain open. Confidence describes category preference, not the chance of solving a coding task.

For the primary untuned/tuned comparison, use the same taxonomy, context rules, GPT pool, and frozen category-to-configuration mapping. This makes differences attributable to classifier adaptation under that policy. Independently refitting a policy for each classifier would be a separate system-level experiment and must be labeled accordingly. Freeze the shared mapping before final checkpoint comparison/selection and held-out evaluation; any earlier joint design search stays within training/development data and is recorded.

## Two kinds of training evidence

**Category supervision:** OpenJev adaptation needs reviewed labels for task type and the selected signals, based only on the current prompt. Annotators must use that same restricted view, even when the dataset also stores execution history or results. The proposed low-cost start is a small manually reviewed annotation set with written definitions, ambiguity/unknown handling, and a documented review process. Who reviews, initial size, quality checks, and any later model-assisted labeling remain open. Do not automatically equate the winning GPT configuration with a semantic category.

**Routing-performance evidence:** Measured candidate outcomes establish which configurations are reliable and economical for the category/signal states. Keep executable success, failures, costs, uncertainty, and all-failure cases. Those records inform the policy; they are not ground-truth task-type annotations. No held-out outcomes may set categories, labels, mapping entries, thresholds, or checkpoints.

Fine-tune OpenJev using category-option supervision under its verified readout convention; a small adapter and conditional quantization remain the training direction. Evaluate classification agreement as a diagnostic and executable coding success/cost as the product outcome. Improved category accuracy does not guarantee better routing.

## Evaluation contract to preserve

Run the classifier and policy before the coding turn, then grade the resulting patch using the pinned isolated [SWE-bench evaluator](https://www.swebench.com/SWE-bench/guides/evaluation/). Use matched tasks, harness, limits, and configuration pool across strategies. Report success first, then cost, tokens, latency, and failures. Include all classification questions and retries in operational cost; record annotation, collection, tuning, hosting, and benchmark compute separately.

Report how often fine-tuning changes categories and final routes, together with fallback rates and classification errors on independently reviewed labels where available. Avoid treating a predicted category's own score as its correctness. Apply the same prompt-only boundary to every classifier and matched rule/learned control. Hidden checks, earlier conversation, and future turns remain outside classifier inputs. Multi-turn results measure rerouting from each current prompt, including vague follow-ups; they do not establish that Jev monitors the execution history.

## Remaining Phase 1 decisions

| Contract | Current state | Next work |
| --- | --- | --- |
| Classification then routing | Confirmed by owner | Preserve this boundary throughout implementation and evaluation. |
| Task type plus signals | Confirmed structure; draft labels above | Review development examples, settle definitions, unknown/mixed handling, and a labeling process. |
| Classifier input | Confirmed prompt-only; first-build size/error defaults selected | Validate provider-specific limits when adding real adapters; keep Codex context separate. |
| Ambiguous prompt handling | Automatic fallback; fixture default and error rules selected | Choose the real reliable fallback from access checks and development evidence. |
| Policy and registry | Offline lookup/eligibility contracts selected | Replace fixture entries with measured mapping and verified live settings before real routing. |
| Terminal/session behavior | Offline state/queue/approval/cancellation defaults selected | Verify compatible published SDK/runtime and protocol behavior before the real adapter. |
| Limits and accounting | Offline deadlines, zero retries, reservations, and $0 external-spend default selected | Review exact run estimates and stage caps before live work; cloud cash remains below $50 cumulatively. |
| Training/evaluation records | Category labels and routing outcomes separated | Fix manifests, grouped splits, annotation provenance, policy calibration, isolation, and reproducibility metadata. |
| Study analysis | Tuned/untuned primary contrast; correctness first | Specify final reliability margin, uncertainty analysis, and affordable sample using development evidence. |

The first offline slice has a concrete contract and may begin when development resumes tomorrow. Phase 1's broader live/research specification is not complete; resolve each remaining gate before its dependent work. The master [Development plan](development-plan.md) governs later integration, measurement, training, and evaluation.

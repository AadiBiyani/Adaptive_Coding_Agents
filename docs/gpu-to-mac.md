# Take the OpenJev run from the RTX 3060 to the Mac

Start with the synthetic run while the PC is available. Repeat the transfer with the selected research checkpoint after training. The owner runs the training commands. All classifier commands here use local inference. The public model and package downloads need internet access.

## 1. Practice the restore with the existing smoke run

1. **On the PC**, open OneDrive **in a browser** with the account used for Desktop backup. Look in `Desktop/Adaptive_Coding_Agents/runs/openjev/smoke-20261125-113447`. Check that `step.json`, `reload.json`, `adapter/adapter_config.json` and `adapter/adapter_model.safetensors` are present. If the folder is missing, allow the sync to finish or upload just that run folder to a private OneDrive folder you control. Keep the original PC files.
2. **On the Mac**, download the entire smoke folder through the browser. Unzip it in Finder and place it at `runs/openjev/smoke-20261125-113447` inside your Mac checkout. Downloading independently tests retrieval from OneDrive. The steps below assume you are in the checkout root. Get the matching training code on the Mac. If `training/openjev/check_mac_adapter.py` is still local to the PC branch, copy that file from OneDrive into the same path in the Mac checkout.
3. **In Mac Terminal**, use an ARM-native Python 3.12 installation for these commands:

   ```bash
   python3.12 -m venv .cache/mac-adapter
   PY="$PWD/.cache/mac-adapter/bin/python"
   "$PY" -m pip install numpy 'safetensors==0.8.0'
   SMOKE=runs/openjev/smoke-20261125-113447
   SMOKE_SHA=21c4877909c1084eff8429b4116404c4d4ad56c7a1c4ebda38b1d22ee45fd375
   "$PY" training/openjev/check_mac_adapter.py "$SMOKE/adapter" --sha256 "$SMOKE_SHA"
   ```

   **Pass:** an exact digest match and a report of **32 tensors and 1,114,112 parameters**. This reads every tensor, validates its shape against the LoRA config, and checks its values are finite. A digest mismatch means the file differs from the source. Recheck the selected run and repeat the download.

4. **For live routing on Apple silicon**, also do a model-level check while the 3060 is available. The small transfer check above requires no base weights. This additional test downloads the approximately 9.5 GB text-only MLX base and uses the original LoRA tensors in memory. Quit memory-heavy apps on the 16 GB Mac. In the same Mac terminal:

   ```bash
   "$PY" -m pip install 'mlx==0.32.2' 'mlx-lm==0.31.3' 'transformers==5.17.0' 'huggingface-hub==1.32.0'
   MLX_BASE="$PWD/models/OpenJev-Flash-9B-MLX"
   .cache/mac-adapter/bin/hf download openjev/OpenJev-Flash-9B-MLX \
     --revision d4709a169392d36a3d6ad79592bfe7f4cadcad83 --local-dir "$MLX_BASE"
   "$PY" training/openjev/check_mac_adapter.py "$SMOKE/adapter" --sha256 "$SMOKE_SHA" \
     --mlx-base "$MLX_BASE" > "$SMOKE/mac-mlx.json" && cat "$SMOKE/mac-mlx.json"
   ```

   **Inspect:** both sets of option scores must be finite, and `option_scores_changed` should be true. Compare the three label choices and policy route with `step.json`. On CUDA the smoke prompt selected `fix / supporting_details / localized` and `luna-low` both before and after applying the adapter. Record any disagreements. CUDA NF4 and MLX 8-bit are different inference configurations. Exact logit equality applies to the original same-runtime reload. This Mac probe uses one fixture and still needs execution on the Mac; broader runtime validation uses frozen development prompts.

   References: [OneDrive folder downloads](https://support.microsoft.com/en-us/onedrive/download-files-and-folders-from-onedrive-or-sharepoint), [OpenJev's MLX release](https://huggingface.co/openjev/OpenJev-Flash-9B-MLX), [MLX-LM LoRA projection layout](https://github.com/ml-explore/mlx-lm/blob/v0.31.3/mlx_lm/tuner/lora.py).

## 2. Freeze the research inputs on the PC

1. The pre-training snapshot for this PC is already saved. From the checkout root, set the following paths and inspect its runtime record. Keep the snapshot intact; if code or dependencies change, identify the version actually used at baseline. Keep private data, adapters and keys outside Git. Use a new run directory per experiment.

   ```powershell
   $py = ".\.cache\flash-env\Scripts\python.exe"
   $uv = ".\.cache\tools\uv.exe"
   $study = ".\runs\openjev\study-1"
   $envRecord = ".\runs\openjev\environment-study-1"
   Get-Content "$envRecord/runtime.json"
   git status --short
   ```

   The frozen package list describes the Windows CUDA environment. The Mac uses the separate environment in step 1. The Windows CUDA wheel originally used was `torch-2.13.0+cu130-cp312-cp312-win_amd64.whl` from the official PyTorch cu130 index.

2. The owner reviewed all 84 active training prompts across 42 issues. The first 12 accepted rows are in `data/review/training-evidence-review.csv`. The next 72 are in six 12-row sheets under `data/review/batches/training-01.csv` through `training-06.csv`. Each sheet contains one prompt per issue, and both variants of an issue belong to the training split. Two older rows remain excluded from the experiment. The private `data/review/review-manifest.json` identifies the final reviewed files and split hashes.
3. For an assistant training draft, show the annotator **one exact prompt at a time**. For example, `& $py training/openjev/dataset.py prompt --id T01` prints that prompt alone. Supply the fixed taxonomy definitions separately. Keep the ID, group, neighboring turns, earlier annotations and outcomes outside the annotator's task input. For each field with a label other than `unknown`, copy a short verbatim span into the corresponding `*_quote` column. Include a span for `mixed_or_unclear`. Leave missing-evidence quotes empty. A reported symptom can support evidence even when scope is unknown. A proposed test with a desired outcome alone does not document an observed failure.

   Review the labels and quotes against the full prompt in each new training sheet. Correct any unsupported labels or quotes. Set `review_status` to `human_reviewed` only on rows you accept. The importer skips pending assistant drafts, validates each accepted quote and retains it in the row's review metadata. Only the prompt and the fixed questions enter the classifier.

   The owner independently labeled all 20 development and 20 held-out prompts before scoring. The private five-row sheets use opaque IDs and preserve the original pilot assignments. To import accepted training rows after editing a UTF-8 sheet, run the following from the project root.

   ```powershell
   foreach ($sheet in Get-ChildItem data/review/batches/training-*.csv) {
       & $py training/openjev/dataset.py record --split training --sheet $sheet.FullName --reviewer owner
       if ($LASTEXITCODE -ne 0) { throw "Training review import failed for $($sheet.Name)" }
   }
   & $py training/openjev/dataset.py audit
   ```

   Before baseline, all active training and development rows must show reviewed. Before held-out scoring, all 20 held-out rows must show reviewed. Keep independent gold labels separate from model outputs.
4. The November 26 pilot uses the private `data/frozen-benchmark-prompts.json` array with six original issue messages and six scripted follow-ups. Keep `data/frozen-benchmark-scenarios.json` alongside it for the pinned tasks, issue groups, input hashes, visible branch rules and sampling record. Only the message array goes to `cache-prompts`. Newly generated follow-ups require a live inference path later.

## 3. Run the matched experiment yourself on the RTX 3060

Run each command separately. Here `baseline` scores untuned Flash on development prompts, `train` creates a fresh adapter and selects the best epoch using development macro-F1, and `held-out` reloads the frozen checkpoint and grades both variants on all 20 prompts.

```powershell
& $py -u training/openjev/experiment.py baseline --run $study
```

Inspect `contract.json`, `git.json`, and `base-development.json`. Confirm the model revision, split hashes, code revision, and 20 development rows. Then start training:

```powershell
& $py -u training/openjev/experiment.py train --run $study
```

Inspect the epoch reports and `freeze.json`, including the selected epoch and adapter hashes. If interrupted, `train --run $study --resume` resumes from a completed epoch. Score held-out once after freezing:

```powershell
& $py -u training/openjev/experiment.py held-out --run $study
```

Check `held-out/comparison.json` for 20 paired rows, each variant's per-field metrics, exact matches out of 20, changed labels and changed model or effort. Keep failed attempts. Preserve the split and freeze when reporting a negative result.

## 4. Export the predictions you will need away from the GPU

1. Score the previously frozen SWE-bench and scripted messages with both variants:

   ```powershell
   & $py -u training/openjev/experiment.py cache-prompts --run $study --prompts data/frozen-benchmark-prompts.json
   ```

   Inspect `cached-prompts/<fingerprint>/base.json`, `tuned.json`, `inputs.json` and `comparison.json`. Check every intended message ID and prompt hash appears in both prediction files. Preserve the original message manifest in the handoff. These cached labels allow later coding runs for those exact messages. The SWE-bench patch generator, isolated grader integration and multi-turn controller remain separate work.

2. Save a small reference set for Mac inference, using the synthetic prompt plus development examples (including changed routes if observed). This example exports the synthetic fixture and all 20 development prompts and starts a **new process** to score them with the selected adapter:

   ```powershell
   $env:PYTHONPATH = "training/openjev"
   & $py -c "from dataset import splits; from smoke import PROMPT; from flash import write, ROOT; rows=[{'id':'smoke-fixture','prompt':PROMPT}]+[{k:r[k] for k in ('id','prompt')} for r in splits()['development']]; write(ROOT/'data/mac-reference-prompts.json', rows)"
   & $py -u training/openjev/experiment.py cache-prompts --run $study --prompts data/mac-reference-prompts.json
   ```

   Match IDs in the reloaded `tuned.json` against the selected epoch's `development.json`. Verify the three labels and routes, and compare the option logits against the original CUDA run (use the smoke check's predeclared 0.02 absolute tolerance on this same runtime). Save that comparison. The MLX probe in step 1 reads the `smoke-fixture` prompt; retain the other rows for validating subsequent live-router integration.

## 5. Pack the research run, then verify it from OneDrive

1. Identify the actual selected epoch and compare its weight checksum to the freeze before packing:

   ```powershell
   $freeze = Get-Content "$study/freeze.json" -Raw | ConvertFrom-Json
   $selected = "$study/epoch-$($freeze.epoch)"
   foreach ($name in "adapter_model.safetensors", "adapter_config.json") {
       $actual = (Get-FileHash -LiteralPath "$selected/$name" -Algorithm SHA256).Hash.ToLowerInvariant()
       if ($actual -ne $freeze.adapter.$name) { throw "Frozen file differs: $name" }
   }
   ```

2. Build a **private** ZIP from explicit paths. Include your separate scenario/task mapping from step 2 if it has a different filename. Save the exact code alongside the run; `git archive` takes the committed source revision. Use a fresh archive name if a previous handoff exists.

   ```powershell
   $rev = (Get-Content "$study/git.json" -Raw | ConvertFrom-Json).revision
   git archive --format=zip -o "$study/committed-source.zip" $rev
   if ($LASTEXITCODE -ne 0) { throw "Source archive failed" }
   $handoffFiles = @($study, $envRecord, "data/openjev-training.json", "data/classifier-pilot.json",
                     "data/review/batches", "data/review/training-evidence-review.csv", "data/review/review-manifest.json",
                     "data/frozen-benchmark-prompts.json", "data/frozen-benchmark-scenarios.json",
                     "data/mac-reference-prompts.json")
   $archive = ".\runs\openjev\study-1-handoff.zip"
   Compress-Archive -LiteralPath $handoffFiles -DestinationPath $archive -ErrorAction Stop
   Get-FileHash -Algorithm SHA256 -LiteralPath $archive | Format-List Hash
   ```

   Keep the **whole handoff ZIP** checksum in a separate note you can read from the Mac. Keep the selected adapter hash from `freeze.json` too. The pinned base, tokenizer and helper can be downloaded again using the model revision in `contract.json` and the pinned downloader. The package should contain the private reviewed rows, selected weights and config, contract, environment, source, checkpoints, reports and both sets of predictions. Credentials and the Windows virtual environment stay out of this archive.

3. Verify the new ZIP is visible in the **OneDrive web interface**. Download the ZIP itself on the Mac. In Terminal run `shasum -a 256 ~/Downloads/study-1-handoff.zip` and compare with the PC's whole-archive digest. Unzip it into a private folder. Locate `study-1/freeze.json`, then open the `epoch-N` directory named by its `epoch` field. Use the final adapter's digest from the PC (the smoke digest belongs to the disposable adapter).
4. From the Mac checkout run `"$PY" training/openjev/check_mac_adapter.py /path/to/study-1/epoch-N --sha256 YOUR_FINAL_DIGEST`. For a live Mac check, repeat with `--mlx-base "$MLX_BASE"` and compare its fixture outputs to the GPU `smoke-fixture` reference for **the same final adapter**. Keep the Mac output with the downloaded research run. If native inference differs or fails, preserve the diagnostics and use the frozen CUDA predictions for fixed-message experiments.

**Before leaving the PC:** confirm the Mac can independently retrieve the private archive, match its digest, read the frozen adapter, open the 20-row held-out reports and find matched predictions for every planned fixed benchmark message. If the Mac is elsewhere, test downloading the ZIP on another device now and mark the actual Mac checks pending. Keeping the source accessible until the Mac restore succeeds gives you a recovery path.

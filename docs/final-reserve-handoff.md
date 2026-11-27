# Final SWE-bench reserve and Mac restoration

The November 27 supplement extends the original private Study 1 handoff. The original ZIP remains the authoritative record for the classifier experiment. The supplement carries a disjoint 48-group downstream reserve, six controlled scenarios, their sealed CUDA predictions, and the code used to produce and check them. Both archives belong in private storage.

## Freeze and evidence

The authoritative inputs are in `data/final-reserve-v1/`. `reserve.json` records the ordered issue groups, original base commits, source revision, dataset revision and hashes. `screening-ledger.json` accounts for the 500 pinned rows. `screening-decisions.json` holds prompt-only review decisions through the cutoff. `initial-prompts.json` holds the original messages, with whitespace preserved after JSON decoding. `scenario-specs.json`, `scenarios.json` and `followup-prompts.json` record the public checks, controller and exact follow-ups. The six probes compiled. Their behavior in isolated task environments still requires validation.

The frame was the default test split of SWE-bench Verified at `78f471bf655a3137b2e8a75af1501690ec009ec3`. The selector verified the raw Parquet SHA-256, then read seven allowed columns. It ranked repositories and their issue queues separately using SHA-256 with the literal salt `ACA-E005-final-v1`. Each round took the next eligible group from each available repository. Eligibility used original public defect reports, the 16,384-byte and three 512-token input limits, development exclusions, similarity flags and recorded semantic reviews. Some relationships may be invisible from the public report. The target population is eligible short reports from these repositories.

The frozen rule in `sample-rule.json` allows prefixes of 12, 24, 36 or 48. Twenty-four is a budgeting placeholder. Before accessing final outputs, record the prefix, spending cap, target precision, reliability margin, retry/failure policy, analysis and decision date using development pilot information only. Preserve tasks with identical routes, failures, and all costs. Six preselected scenarios have a mandatory second message and at most one conditional corrective message. Both new caches include all possible scripted branches.

## Blinding and receipts

`runs/openjev/final-reserve-cache-v1/verification/` contains the two blind receipts, pre-inference token/hash records, selection replay, environment, timings and attempt records. The sealed cache files and logs contain final outputs. Only the checker should read those outputs before the size and analysis decisions are signed. Use the 21 Mac reference messages and 12 development-pilot messages for debugging. The archives use ordinary ZIP and procedural blinding. Restrict OneDrive and local file access to the research team.

The Windows verifier checks both variants independently against precomputed prompt and formatted-token hashes and lengths. It checks order, shape, finite values, probability normalization, contract and freeze bindings, and the four output file hashes per cache pair. The payload inventory and whole-ZIP hashes bind the full original and supplement. The first initial-cache attempt stopped during Windows model loading. Its process record, private logs and input-only partial cache are included. Separate preflight and scoring processes completed the same frozen job.

Process records contain elapsed wall time, execution order and sampled whole-device memory. Each private prediction row has a scoring timer; aggregate timings are stored in the corresponding timing JSON. The frozen implementation has no dedicated load timer or PyTorch allocated/reserved-memory instrumentation for cache exports. Runtime comparisons should account for process startup, prompt lengths and the untuned-first order.

## Replaying the selection on Windows

Use a separate checkout/workspace at the Git revision in `reserve.json` with the exact working files, private source datasets and tokenizer from the handoff. Use the frozen CUDA Python environment for tokenizer compatibility and PyArrow 20.0.0 for Parquet projection. The original public release is downloadable at its recorded revision. The full Parquet and the disposable projected scratch are unnecessary for cache lookup on the Mac. The following replay is for an investigator checking methods. Final GPU exports already exist.

```powershell
$py = ".\.cache\flash-env\Scripts\python.exe"
& $py -B training/openjev/reserve_select.py prepare
& $py -B training/openjev/reserve_replay.py
```

Run `prepare` only in a fresh replay workspace with no previous projected scratch. It requires the pinned public dataset, local tokenizer files and PyArrow. The replay uses the fixed screening decisions and compares the reconstructed freeze with the archived files. The original execution sequence was selector prepare, selector freeze, cache init and initial run, scenario freeze and followup run, offline replay, then package build. Each GPU run used `experiment.py cache-prompts` with a private output redirect. Avoid rerunning scoring to check archived predictions.

## Restore both ZIPs on the Mac

Download both ZIPs and their adjacent `.zip.sha256` files through the OneDrive web interface in **My files → Desktop → Adaptive_Coding_Agents → runs → openjev**. Leave each filename unchanged and place the four files in Downloads. Compare the two expected digest strings with the Windows completion record, independent of the downloaded sidecars. Start with an empty private folder on native ARM64 macOS 14 or later, with Python 3.12 installed. Run in a single terminal:

```sh
set -eu
umask 077
cd "$HOME/Downloads"
shasum -a 256 -c study-1-handoff.zip.sha256
shasum -a 256 -c study-1-final-reserve-v1-supplement.zip.sha256
mkdir -p "$HOME/Research"
RESTORE=$(mktemp -d "$HOME/Research/openjev-study-1.XXXXXXXX")
unzip -q study-1-handoff.zip -d "$RESTORE"
unzip -q study-1-final-reserve-v1-supplement.zip -d "$RESTORE"
cd "$RESTORE"
python3.12 -B training/openjev/reserve_handoff.py verify-restored
python3.12 -c 'import platform,sys; assert platform.machine()=="arm64" and sys.version_info[:2]==(3,12)'
python3.12 -m venv .mac-venv
PY="$PWD/.mac-venv/bin/python"
"$PY" -m pip --isolated --disable-pip-version-check install --no-index --find-links handoff/wheels --require-hashes -r handoff/requirements-macos-mlx.lock
"$PY" -m pip check
"$PY" -B training/openjev/check_mac_adapter.py runs/openjev/study-1/epoch-2 --sha256 4df1aabb56df5decfcf5c006dbbd3cb6d7eb2ba15b39fd1156c6af11d51fead0 > mac-adapter-integrity.json
"$PY" -c 'import json; x=json.load(open("mac-adapter-integrity.json")); assert (x["tensors_read"],x["parameters_read"])==(32,1114112); print("Adapter tensor count and parameter count passed.")'
pwd
```

The standard-library checker verifies every member against the two internal inventories, the original and copied contract files, the selection records and both sealed caches. Its only classifier-related output is blind counts, integrity digests and pass/fail. The adapter check reads every tensor. Save the fresh destination path and receipts as evidence. A Windows restore rehearsal cannot replace a Mac download and verification.

## Remaining research work

1. Complete and record the physical Mac restore.
2. For E007b, validate base and adapted MLX independently using the development references. The existing checker exercises one fixture. Implement the full panel comparison for both variants, matching input tokens, candidate order, margins, labels and routes. Freeze the portability criterion before inspecting native results. The proposed Mac backend uses the pinned public 8-bit MLX model at `d4709a169392d36a3d6ad79592bfe7f4cadcad83`. The authoritative study uses the CUDA NF4 parent at `b77b0fff67c77a76c16d4da50a66d2fdbc124fae`. The original training contract, adapter and working source are in the first archive.
3. Build exact lookup by manifest fingerprint, message ID, raw hash, variant, freeze and policy version. Enforce one lookup per new scripted message and keep coding-session history with the coding agent. Test with the development pilot. Preserve cache-miss and integrity errors.
4. Validate the common coding harness and isolated SWE-bench grader on development tasks, including original-task regression checks, public branch probes, resource ceilings, failure classification and telemetry. Use pinned grader images/versions and keep grading information outside the coding workspace. Freeze the controller and validation rules. Avoid using independent outcomes to tune either system.
5. Obtain approval for any paid runs. Execute the six-issue development coding pilot, estimate costs and paired variability, then sign the prefix and analysis decisions before unsealing the reserve. Run the matched independent strategies on the same assigned tasks. Analyze executable resolution, cost per attempted/resolved issue, latency, tokens, failures and paired issue-level uncertainty.
6. Model-only, effort-only and initial-only versus per-turn routing can reuse predictions for these exact messages. Compare the controls needed for each paper claim. Separate conditional script behavior from organic multi-turn use. No further fine-tuning or CUDA session is needed for these frozen inputs. New free-text turns need a validated inference backend or additional authoritative CUDA predictions.

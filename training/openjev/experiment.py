"""Owner-operated Flash 9B study. Commands run one stage at a time."""

import argparse
from dataclasses import asdict
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import subprocess
from time import perf_counter

from dataset import FIELDS, require_review, split_hashes, splits
from flash import (MAX_LENGTH, MODEL_ID, REVISION, ROOT, SEED, TEMPERATURE, Readout,
                   add_adapter, candidate_loss, load_base, sha, verify_model, write)
from adaptive_coding_agents.classifier_dataset import fingerprint, summarize
from adaptive_coding_agents.records import Labels, PromptRecord
from adaptive_coding_agents.routing import POLICY_VERSION, select_route
from adaptive_coding_agents.taxonomy import TAXONOMY_VERSION, category_questions

EPOCHS = 2
ACCUMULATION = 8
LR = 1e-4


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def contract(data):
    import torch
    files = [Path(__file__), Path(__file__).with_name("flash.py"), Path(__file__).with_name("dataset.py")]
    package = ROOT / "backend/src/adaptive_coding_agents"
    files += [package / name for name in ("classifier_dataset.py", "records.py", "routing.py", "taxonomy.py")]
    return {"model": MODEL_ID, "revision": REVISION, "temperature": TEMPERATURE, "labels": list(FIELDS),
            "choice_order": {k: list(v) for k, v in Labels.OPTIONS.items()},
            "taxonomy": TAXONOMY_VERSION, "questions_hash": fingerprint(category_questions()),
            "policy": POLICY_VERSION, "split_hashes": split_hashes(data),
            "code_hashes": {f.name: sha(f) for f in files}, "max_tokens": MAX_LENGTH,
            "environment": {p: importlib.metadata.version(p) for p in
                            ("torch", "transformers", "peft", "bitsandbytes", "accelerate", "tokenizers")},
            "gpu": torch.cuda.get_device_name(), "python": platform.python_version(),
            "cuda": torch.version.cuda, "seed": SEED, "epochs": EPOCHS, "microbatch": 1,
            "gradient_accumulation": ACCUMULATION, "learning_rate": LR,
            "quantization": "NF4 double quant, bfloat16 compute", "rank": 8, "alpha": 16,
            "targets": "NF4 full-attention q_proj/v_proj in language_model.layers",
            "optimizer": "AdamW, weight_decay=0, constant LR, grad norm cap=1"}


def score(model, reader, rows):
    import torch
    model.eval()
    predictions, losses = [], []
    with torch.inference_mode():
        for row in rows:
            start = perf_counter()
            fields, predicted = {}, {}
            for f, choices in reader.choices.items():
                ids = reader.encode(row["prompt"], f)
                logits = reader.logits(model, ids, f)
                if not torch.isfinite(logits).all():
                    raise ValueError(f"Nonfinite score at {row['id']} / {f}")
                predicted[f] = choices[int(logits.argmax())]
                fields[f] = {"logits": logits.tolist(), "probabilities": (logits / TEMPERATURE).softmax(0).tolist(),
                             "formatted_ids_sha256": fingerprint(ids), "tokens": len(ids)}
                if row.get("labels"):
                    losses.append(candidate_loss(logits, choices.index(row["labels"][f])).item())
            route = select_route(Labels.from_dict(predicted))
            predictions.append({"id": row["id"], "group_id": row.get("group_id"),
                                "prompt_sha256": PromptRecord.capture(row["prompt"]).prompt_sha256,
                                "expected": row.get("labels"), "predicted": predicted, "status": "ok",
                                "elapsed_seconds": perf_counter()-start, "fields": fields,
                                "route": asdict(route.configuration), "fallback": route.fallback})
    result = {"rows": predictions}
    if losses:
        metrics = summarize(predictions)
        result.update(metrics=metrics, mean_loss=sum(losses)/len(losses),
                      mean_macro_f1=sum(v["macro_f1"] for v in metrics["fields"].values())/len(FIELDS),
                      exact_match_count=sum(r["expected"] == r["predicted"] for r in predictions))
    return result


def adapter_hash(path):
    return {n: sha(path / n) for n in ("adapter_model.safetensors", "adapter_config.json")}


def train(out, reader, data, resume):
    import torch
    from peft import PeftModel
    rows = data["training"]
    require_review(rows)
    previous = [e for e in range(1, EPOCHS+1) if (out / f"epoch-{e}/done.json").is_file()]
    if previous and not resume:
        raise ValueError("Use --resume to continue from a completed epoch")
    epoch0 = max(previous, default=0)
    if epoch0:
        path = out / f"epoch-{epoch0}"
        base = load_base()
        base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model = PeftModel.from_pretrained(base, path, is_trainable=True)
    else:
        model = add_adapter(load_base())
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=LR, weight_decay=0.)
    if epoch0:
        opt.load_state_dict(torch.load(path/"optimizer.pt", map_location="cuda", weights_only=True))
    decisions = [(r["id"], f, reader.encode(r["prompt"], f), reader.choices[f].index(r["labels"][f]))
                 for r in rows for f in FIELDS]
    for epoch in range(epoch0+1, EPOCHS+1):
        path = out / f"epoch-{epoch}"
        path.mkdir(exist_ok=True)
        model.train()
        order = random.Random(SEED + epoch).sample(decisions, len(decisions))
        history = []
        for start in range(0, len(order), ACCUMULATION):
            batch = order[start:start+ACCUMULATION]
            opt.zero_grad(set_to_none=True)
            for ident, f, ids, target in batch:
                loss = candidate_loss(reader.logits(model, ids, f), target)
                if not torch.isfinite(loss):
                    raise ValueError(f"Nonfinite training loss at {ident} / {f}")
                (loss/len(batch)).backward()
                history.append(loss.item())
            norm = torch.nn.utils.clip_grad_norm_(params, 1., error_if_nonfinite=True)
            opt.step()
            print(f"epoch {epoch}, decisions {start+len(batch)}/{len(order)}, "
                  f"loss {sum(history[-len(batch):])/len(batch):.4f}, grad norm {norm.item():.4f}", flush=True)
        result = score(model, reader, data["development"])
        model.save_pretrained(path, save_embedding_layers=False)
        torch.save(opt.state_dict(), path / "optimizer.pt")
        write(path / "development.json", result)
        write(path / "done.json", {"epoch": epoch, "adapter": adapter_hash(path),
                                   "development_sha256": sha(path/"development.json"),
                                   "loss_by_decision": history, "mean_macro_f1": result["mean_macro_f1"],
                                   "mean_loss": result["mean_loss"]})
    checkpoints = [read(out/f"epoch-{e}/done.json") for e in range(1, EPOCHS+1)]
    best = max(checkpoints, key=lambda c: (c["mean_macro_f1"], -c["mean_loss"], -c["epoch"]))
    write(out / "freeze.json", {"epoch": best["epoch"], "adapter": best["adapter"],
                                "contract": sha(out/"contract.json"), "selection": checkpoints})
    print(f"Frozen epoch {best['epoch']}, mean development macro-F1 {best['mean_macro_f1']:.4f}")


def compare(out, reader, rows, dest):
    from peft import PeftModel
    freeze = read(out / "freeze.json")
    adapter = out / f"epoch-{freeze['epoch']}"
    if freeze["contract"] != sha(out/"contract.json") or freeze["adapter"] != adapter_hash(adapter):
        raise ValueError("Frozen contract or adapter changed")
    dest.mkdir(parents=True, exist_ok=False)
    write(dest/"inputs.json", {"rows_sha256": fingerprint(rows), "freeze_sha256": sha(out/"freeze.json")})
    base = load_base()
    first = score(base, reader, rows)
    write(dest/"base.json", first)
    tuned = score(PeftModel.from_pretrained(base, adapter), reader, rows)
    write(dest/"tuned.json", tuned)
    pairs = list(zip(first["rows"], tuned["rows"], strict=True))
    result = {"n": len(rows), "changed_labels": sum(a["predicted"] != b["predicted"] for a,b in pairs),
              "changed_model": sum(a["route"]["model"] != b["route"]["model"] for a,b in pairs),
              "changed_effort": sum(a["route"]["effort"] != b["route"]["effort"] for a,b in pairs),
              "changed_model_or_effort": sum(a["route"]["id"] != b["route"]["id"] for a,b in pairs)}
    for label, report in (("base", first), ("tuned", tuned)):
        if "metrics" in report:
            result[label] = {"exact_match_count": report["exact_match_count"], **report["metrics"]}
    write(dest/"comparison.json", result)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("baseline", "train", "held-out", "cache-prompts"))
    parser.add_argument("--run", type=Path, default=ROOT / "runs/openjev/study-1")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--prompts", type=Path, help="Frozen JSON array with id and prompt for each message")
    args = parser.parse_args()
    out = args.run
    data = splits()
    require_review(data["training"])
    require_review(data["development"])
    if args.stage == "held-out":
        require_review(data["held_out"])
    current = contract(data)
    reader = Readout()
    if args.stage == "baseline":
        verify_model(full=True)
        out.mkdir(parents=True, exist_ok=False)
        write(out/"contract.json", current)
        write(out/"git.json", {"revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()})
        write(out/"base-development.json", score(load_base(), reader, data["development"]))
    elif read(out/"contract.json") != current or not (out/"base-development.json").is_file():
        raise ValueError("Run baseline first with the same reviewed data, code and environment")
    elif args.stage == "train":
        if (out/"freeze.json").exists():
            raise ValueError("Adapter already frozen")
        train(out, reader, data, args.resume)
    elif args.stage == "held-out":
        compare(out, reader, data["held_out"], out/"held-out")
    else:
        if not args.prompts:
            parser.error("Supply --prompts with an already frozen manifest")
        rows = read(args.prompts)
        if not rows or any(set(r) != {"id","prompt"} for r in rows) or len({r["id"] for r in rows}) != len(rows):
            raise ValueError("Expected unique id/prompt pairs")
        compare(out, reader, rows, out/"cached-prompts"/fingerprint(rows))


if __name__ == "__main__":
    main()

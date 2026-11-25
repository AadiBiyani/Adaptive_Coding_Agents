"""Synthetic-only NF4 feasibility run and independent process reload check."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from flash import (MODEL_ID, REVISION, ROOT, SEED, Readout, add_adapter, candidate_loss,
                   load_base, verify_model, write)
from adaptive_coding_agents.records import Labels
from adaptive_coding_agents.routing import select_route

# Handwritten software fixture only. Never read owner examples or split labels here.
PROMPT = ("In the Python fixture, fix only mark_complete. It calls pending.add(key) "
          "after a successful save. Given a pending set containing the saved key, the "
          "current function leaves it pending and the next pass saves it a second time. "
          "The expected result is that this key disappears while every other pending key remains.")
TARGET = Labels("fix", "supporting_details", "localized")
ATOL = 0.02


def snapshot(model, reader):
    import torch
    model.eval()
    with torch.inference_mode():
        scores = {f: reader.logits(model, reader.encode(PROMPT, f), f).tolist()
                  for f in reader.choices}
    labels = {f: opts[max(range(len(opts)), key=scores[f].__getitem__)]
              for f, opts in reader.choices.items()}
    route = select_route(Labels.from_dict(labels))
    return {"scores": scores, "labels": labels, "route": route.configuration.id}


def reload(out):
    from peft import PeftModel
    model = PeftModel.from_pretrained(load_base(), out / "adapter")
    result = snapshot(model, Readout())
    expected = json.loads((out / "step.json").read_text())["after"]
    delta = max(abs(x-y) for f in expected["scores"]
                for x, y in zip(expected["scores"][f], result["scores"][f], strict=True))
    passed = delta <= ATOL and result["labels"] == expected["labels"] and result["route"] == expected["route"]
    write(out / "reload.json", {"passed": passed, "absolute_tolerance": ATOL, "max_logit_error": delta, **result})
    if not passed:
        raise RuntimeError("Fresh-process scores or routing differ from saved fixture")


def step(out):
    import torch
    out.mkdir(parents=True, exist_ok=False)
    verify_model(full=True)
    torch.cuda.reset_peak_memory_stats()
    model = add_adapter(load_base())
    reader = Readout()
    before = snapshot(model, reader)
    tensors = {f: reader.encode(PROMPT, f) for f in reader.choices}
    params = {name: p for name, p in model.named_parameters() if p.requires_grad}
    initial = {name: p.detach().clone() for name, p in params.items()}
    opt = torch.optim.AdamW(params.values(), lr=1e-4, weight_decay=0.)
    fields = list(reader.choices)
    losses = []
    model.train()
    for i in range(15):
        if i == 3:
            torch.cuda.synchronize()
            start = perf_counter()
        field = fields[i % 3]
        opt.zero_grad(set_to_none=True)
        logits = reader.logits(model, tensors[field], field)
        loss = candidate_loss(logits, reader.choices[field].index(getattr(TARGET, field)))
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(params.values(), 1., error_if_nonfinite=True)
        if not torch.isfinite(loss) or norm.item() == 0:
            raise RuntimeError("Missing or nonfinite loss/gradient")
        opt.step()
        losses.append(loss.item())
        print(f"fixture decision {i+1}/15  {field}  loss={loss.item():.5f}", flush=True)
    torch.cuda.synchronize()
    train_seconds = perf_counter() - start
    changed = [k for k, p in params.items() if not torch.equal(initial[k], p)]
    if not changed or any(p.grad is not None for p in model.parameters() if not p.requires_grad):
        raise RuntimeError("Adapter update or frozen-base check failed")
    torch.cuda.synchronize()
    start = perf_counter()
    after = snapshot(model, reader)
    torch.cuda.synchronize()
    eval_seconds = perf_counter() - start
    start = perf_counter()
    model.save_pretrained(out / "adapter", save_embedding_layers=False)
    save_seconds = perf_counter() - start
    write(out / "step.json", {
        "synthetic_only": True, "model": MODEL_ID, "revision": REVISION, "seed": SEED,
        "device": torch.cuda.get_device_name(), "torch": str(torch.__version__), "cuda": torch.version.cuda,
        "peak_allocated_mib": torch.cuda.max_memory_allocated()/2**20,
        "peak_reserved_mib": torch.cuda.max_memory_reserved()/2**20,
        "formatted_lengths": {f: len(ids) for f, ids in tensors.items()},
        "letter_ids": reader.letters, "base_frozen": True, "changed_adapter_tensors": len(changed),
        "trainable_parameters": sum(p.numel() for p in params.values()), "losses": losses,
        "timed_decisions": 12, "seconds": train_seconds, "decisions_per_second": 12/train_seconds,
        "eval_seconds_per_three_fields": eval_seconds, "adapter_save_seconds": save_seconds,
        "eta_seconds_by_training_prompts": {
            str(n): n*3*2*train_seconds/12 + (3*20+2*20)*eval_seconds + 2*save_seconds
            for n in (80, 100, 120)},
        "eta_assumptions": "Two epochs, base dev plus two tuned dev passes and two held-out passes. Excludes setup, reloads, backup and owner review. Smoke performs an optimizer step every field.",
        "before": before, "after": after})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path)
    parser.add_argument("--stage", choices=["step", "reload"])
    args = parser.parse_args()
    if args.stage == "step":
        step(args.out)
    elif args.stage == "reload":
        reload(args.out)
    else:
        for stage in ("step", "reload"):
            subprocess.run([sys.executable, __file__, str(args.out), "--stage", stage], check=True)
        print((args.out / "step.json").read_text())
        print((args.out / "reload.json").read_text())

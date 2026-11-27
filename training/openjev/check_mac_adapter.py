"""Check a downloaded Flash adapter. Optional MLX inference requires Apple silicon."""

import argparse
import json
import math
from pathlib import Path
import re

from flash import render, sha
from smoke import PROMPT
from adaptive_coding_agents.records import Labels
from adaptive_coding_agents.routing import select_route


def read_adapter(directory, expected_sha):
    import numpy as np
    from safetensors.numpy import load_file

    path = directory / "adapter_model.safetensors"
    if sha(path) != expected_sha.lower():
        raise ValueError("Adapter bytes differ from the GPU copy")
    config = json.loads((directory / "adapter_config.json").read_text(encoding="utf-8"))
    if (config["peft_type"] != "LORA" or config["bias"] != "none" or
            any(config.get(k) for k in ("rank_pattern", "alpha_pattern", "use_dora",
                                        "use_rslora", "fan_in_fan_out", "modules_to_save"))):
        raise ValueError("This check supports the project's ordinary q/v LoRA recipe")
    layers = {}
    weights = load_file(str(path))
    for target in config["target_modules"]:
        match = re.fullmatch(r"model\.language_model\.layers\.(\d+)\.self_attn\.(q_proj|v_proj)", target)
        if not match:
            raise ValueError(f"Unexpected adapter target: {target}")
        prefix = "base_model.model." + target
        a = weights.pop(prefix + ".lora_A.weight")
        b = weights.pop(prefix + ".lora_B.weight")
        if a.ndim != 2 or b.ndim != 2 or a.shape[0] != config["r"] or b.shape[1] != config["r"]:
            raise ValueError(f"Rank mismatch at {target}")
        if not (np.isfinite(a).all() and np.isfinite(b).all()):
            raise ValueError(f"Nonfinite weights at {target}")
        layers[int(match[1]), match[2]] = (a, b)
    if weights or not layers:
        raise ValueError("Adapter tensors and configured targets differ")
    return config, layers


def mac_inference(model_path, config, layers):
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.tuner.lora import LoRALinear
    from transformers import AutoTokenizer

    model, _ = load(str(model_path.resolve()))
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    inputs = {}
    letters = [tokenizer.encode(c, add_special_tokens=False) for c in "ABCD"]
    if letters != [[32], [33], [34], [35]]:
        raise ValueError("Unexpected option token IDs")
    for field in Labels.OPTIONS:
        text = tokenizer.apply_chat_template(render(PROMPT, field), tokenize=False,
                                             enable_thinking=False, add_generation_prompt=True)
        inputs[field] = mx.array([tokenizer.encode(text, add_special_tokens=False)])

    def predict():
        scores, labels = {}, {}
        for field, choices in Labels.OPTIONS.items():
            logits = model(inputs[field])[0, -1]
            values = logits[32:32+len(choices)].astype(mx.float32).tolist()
            if not all(map(math.isfinite, values)):
                raise ValueError(f"Nonfinite {field} scores")
            scores[field] = values
            labels[field] = choices[max(range(len(values)), key=values.__getitem__)]
        return {"scores": scores, "labels": labels, "route": select_route(Labels.from_dict(labels)).configuration.id}

    before = predict()
    # PEFT stores A[r,in] and B[out,r]. MLX multiplies x @ A.T @ B.T.
    for (index, name), (a, b) in layers.items():
        attention = model.layers[index].self_attn
        adapted = LoRALinear.from_base(getattr(attention, name), r=config["r"],
                                       scale=config["lora_alpha"]/config["r"], dropout=0.)
        if adapted.lora_a.shape != a.T.shape or adapted.lora_b.shape != b.T.shape:
            raise ValueError(f"Base/adapter dimension mismatch at layer {index} {name}")
        adapted.lora_a = mx.array(a.T.copy())
        adapted.lora_b = mx.array(b.T.copy())
        setattr(attention, name, adapted)
    model.eval()
    after = predict()
    return {"before": before, "after": after, "option_scores_changed": before["scores"] != after["scores"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter", type=Path)
    parser.add_argument("--sha256", required=True, help="Digest from the source PC")
    parser.add_argument("--mlx-base", type=Path, help="Local pinned OpenJev Flash 9B MLX 8-bit directory")
    args = parser.parse_args()
    config, layers = read_adapter(args.adapter, args.sha256)
    report = {"sha256": args.sha256.lower(), "tensors_read": 2*len(layers),
              "parameters_read": sum(a.size+b.size for a,b in layers.values())}
    if args.mlx_base:
        report.update(mac_inference(args.mlx_base, config, layers))
    print(json.dumps(report, indent=2))
    if report.get("option_scores_changed") is False:
        raise SystemExit("This fixture did not demonstrate a visible adapter effect.")

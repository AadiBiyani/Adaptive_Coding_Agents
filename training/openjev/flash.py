"""Local Flash 9B Choice readout and NF4 adapter setup. Run from the checkout."""

import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend/src"))
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DEACTIVATE_ASYNC_LOAD"] = "1"

from adaptive_coding_agents.records import PromptRecord
from adaptive_coding_agents.taxonomy import category_questions

MODEL_ID = "openjev/OpenJev-Flash-9B"
REVISION = "b77b0fff67c77a76c16d4da50a66d2fdbc124fae"
MODEL = ROOT / "models/OpenJev-Flash-9B"
MANIFEST_HASH = "e260785e815624f1797a56e76e04af3b3d35710c2685213861f146305f8811d1"
TEMPERATURE = 1.07
MAX_LENGTH = 512
SEED = 570


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_model(full=False):
    manifest = MODEL / "MANIFEST.json"
    if sha(manifest) != MANIFEST_HASH:
        raise ValueError("Unexpected upstream manifest")
    for name, entry in json.loads(manifest.read_text()).items():
        if name.startswith(("assets/", "_")) or name == "helper/shim_mlx.py":
            continue
        path = MODEL / name
        if path.stat().st_size != entry["bytes"]:
            raise ValueError(f"Incomplete snapshot file: {name}")
        if (full or path.suffix != ".safetensors") and sha(path) != entry["sha256"]:
            raise ValueError(f"Snapshot checksum mismatch: {name}")


def render(prompt, field):
    PromptRecord.capture(prompt)
    question = category_questions()[field]
    choices = question["criteria"]
    lines = "\n".join(f"[{chr(65+i)}] {key}: {value}" for i, (key, value) in enumerate(choices.items()))
    # Exact text-only branch of helper/shim.py at REVISION (one lettering, no padding).
    content = (f"State:\n{prompt}\n\nQuestion: {question['instructions']}\nOptions:\n{lines}"
               "\n\nAnswer with the letter of the best option only.")
    return [{"role": "user", "content": content}]


class Readout:
    def __init__(self):
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
        self.choices = {k: tuple(q["criteria"]) for k, q in category_questions().items()}
        tokens = [self.tokenizer.encode(c, add_special_tokens=False) for c in "ABCD"]
        if any(len(ids) != 1 for ids in tokens) or len({ids[0] for ids in tokens}) != 4:
            raise ValueError("Option letters must be distinct single tokens")
        self.letters = [ids[0] for ids in tokens]

    def encode(self, prompt, field):
        text = self.tokenizer.apply_chat_template(render(prompt, field), tokenize=False,
                                                  enable_thinking=False, add_generation_prompt=True)
        ids = self.tokenizer.encode(text, add_special_tokens=False)
        if len(ids) > MAX_LENGTH:
            raise ValueError(f"{field} uses {len(ids)} tokens, above the {MAX_LENGTH}-token limit")
        return ids

    def logits(self, model, ids, field):
        import torch
        tokens = torch.tensor([ids], device="cuda")
        output = model(input_ids=tokens, logits_to_keep=1, use_cache=False)
        allowed = self.letters[:len(self.choices[field])]
        return output.logits[0, -1, allowed].float()


def load_base():
    import torch
    from transformers import BitsAndBytesConfig, Qwen3_5ForConditionalGeneration, set_seed
    verify_model()
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("This recipe requires CUDA with bfloat16 support")
    set_seed(SEED)
    config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL, local_files_only=True, device_map={"": 0}, dtype=torch.bfloat16,
        quantization_config=config, attn_implementation="sdpa")
    model.requires_grad_(False)
    return model


def add_adapter(base):
    from peft import LoraConfig, get_peft_model
    from bitsandbytes.nn import Linear4bit
    targets = [name for name, module in base.named_modules()
               if ".language_model.layers." in name and name.endswith((".q_proj", ".v_proj"))
               and isinstance(module, Linear4bit)]
    if not targets:
        raise RuntimeError("No NF4 language-attention q/v projections found")
    base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    adapter = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                         target_modules=targets, task_type="CAUSAL_LM")
    model = get_peft_model(base, adapter)
    trainable = [name for name, p in model.named_parameters() if p.requires_grad]
    if not trainable or any("lora_" not in name for name in trainable):
        raise RuntimeError("Unexpected trainable base weights")
    return model


def candidate_loss(logits, index):
    import torch
    import torch.nn.functional as F
    return F.cross_entropy(logits[None], torch.tensor([index], device=logits.device))


def write(path, value):
    # Each caller owns a new run directory. Publish complete JSON after a successful write.
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")
    tmp.replace(path)

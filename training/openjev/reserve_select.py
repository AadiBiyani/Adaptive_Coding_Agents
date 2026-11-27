"""Build the outcome-blind final reserve from a pinned, column-projected SWE-bench release."""
import argparse
import ast
import collections
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import urlopen

from flash import ROOT, MODEL, MAX_LENGTH, Readout, render, sha
from smoke import PROMPT
from adaptive_coding_agents.classifier_dataset import fingerprint
from adaptive_coding_agents.records import PROMPT_LIMIT_BYTES

SALT = "ACA-E005-final-v1"
DEFAULT = ROOT / "data/final-reserve-v1"
SCRATCH = ROOT / ".cache/final-reserve-selection-v1.json"
PILOT = ROOT / "data/frozen-benchmark-scenarios.json"
RELEASE = "78f471bf655a3137b2e8a75af1501690ec009ec3"
PARQUET = "030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25"
COLUMNS = ["instance_id", "repo", "base_commit", "version", "environment_setup_commit", "image", "problem_statement"]


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def order(kind, ident):
    return digest(f"{SALT}|{kind}|{ident}"), ident


def norm(text):
    return " ".join(re.findall(r"\w+", text.casefold()))


def words(text):
    return re.findall(r"[a-z][a-z_0-9]{2,}", text.casefold())


def shingles(text):
    seq = words(text)
    return set(zip(seq, seq[1:], seq[2:], seq[3:]))


def provenance():
    dev = {}
    sources = {}
    for name in ("openjev-training.json", "classifier-pilot.json", "frozen-benchmark-prompts.json", "mac-reference-prompts.json"):
        path = ROOT / "data" / name
        raw = read(path)
        sources[name] = sha(path)
        for row in raw["examples"] if isinstance(raw, dict) else raw:
            dev[f"{name}/{row['id']}"] = row["prompt"]
    dev["smoke.py/PROMPT"] = PROMPT
    # Additional prompts from development worksheets, including earlier drafts.
    import csv
    for path in sorted((ROOT / "data/review").rglob("*.csv")):
        sources[path.relative_to(ROOT).as_posix()] = sha(path)
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for i, row in enumerate(csv.DictReader(stream)):
                if row.get("prompt"):
                    dev[f"{path.name}/{i+1}"] = row["prompt"]
    return dev, sources


def prepare():
    sys.path.insert(0, str(ROOT / ".cache/benchmark-parquet-reader"))
    import pyarrow as pa
    import pyarrow.parquet as pq
    pilot = read(PILOT)
    upstream = pilot["upstream"]
    need(upstream["revision"] == RELEASE and upstream["artifact_sha256"] == PARQUET, "Upstream pin")
    url = f"https://huggingface.co/datasets/{upstream['dataset']}/resolve/{RELEASE}/{upstream['artifact']}"
    with urlopen(url, timeout=90) as response:
        raw = response.read()
    need(hashlib.sha256(raw).hexdigest() == PARQUET, "Parquet SHA-256")
    rows = pq.read_table(pa.BufferReader(raw), columns=COLUMNS).to_pylist()
    need(len(rows) == len({r["instance_id"] for r in rows}) == 500, "Upstream population")
    dev, sources = provenance()
    reader = Readout()
    field_names = tuple(reader.choices)
    pilot_ids = {t["instance_id"] for t in pilot["tasks"]}
    previous_features = {t["instance_id"] for t in pilot["selection"]["ranked_screen_through_cutoff"]
                         if t["decision"] == "excluded_feature_request"}
    texts = {r["instance_id"]: r["problem_statement"] for r in rows}
    texts.update(dev)
    norms = {k: norm(v) for k,v in texts.items()}
    grams = {k: shingles(v) for k,v in texts.items()}
    dev_words = {k: set(words(v)) for k,v in dev.items()}
    docs = [set(words(r["problem_statement"])) for r in rows]
    df = collections.Counter(w for ws in docs for w in ws)
    records = []
    for row, bag in zip(rows, docs, strict=True):
        ident = row["instance_id"]
        prompt = row["problem_statement"]
        meta = {k: row[k] for k in COLUMNS if k != "problem_statement"}
        nbytes = len(prompt.encode("utf-8"))
        lengths = {}
        if nbytes <= PROMPT_LIMIT_BYTES:
            for field in field_names:
                text = reader.tokenizer.apply_chat_template(render(prompt, field), tokenize=False,
                    enable_thinking=False, add_generation_prompt=True)
                lengths[field] = len(reader.tokenizer.encode(text, add_special_tokens=False))
        exact = [k for k in norms if k != ident and norms[k] == norms[ident]]
        near = []
        for k, g in grams.items():
            if k == ident or not g or not grams[ident]:
                continue
            inter = len(g & grams[ident]); union = len(g) + len(grams[ident]) - inter
            if inter >= 4 and (inter / union >= .2 or inter / min(len(g),len(grams[ident])) >= .55):
                near.append(k)
        rare = {w for w in bag if df[w] <= 3 and len(w) >= 5}
        topical = sorted({k for k,v in dev_words.items() if len(rare & v) >= 2})
        cited = []
        for k in texts:
            if k == ident or "__" not in k or "/" in k:
                continue
            repo, num = k.rsplit("-",1)
            if not num.isdigit(): continue
            same_repo = repo.replace("__","/") == row["repo"]
            if (same_repo and re.search(r"(?:#|/(?:issues|pull)/)" + num + r"(?!\d)", prompt)) or re.search(re.escape(repo.replace("__","/")) + r"(?:#|/(?:issues|pull)/)" + num + r"(?!\d)", prompt, re.I):
                cited.append(k)
        if ident in pilot_ids: gate = "development_pilot"
        elif nbytes > PROMPT_LIMIT_BYTES: gate = "over_byte_limit"
        elif max(lengths.values()) > MAX_LENGTH: gate = "over_token_limit"
        elif ident in previous_features: gate = "previously_screened_feature"
        elif any(k in dev or k in pilot_ids for k in exact): gate = "exact_development_duplicate"
        else: gate = "needs_review"
        records.append(dict(meta,prompt=prompt,prompt_sha256=digest(prompt),utf8_bytes=nbytes,
            formatted_tokens=lengths,gate=gate,exact=exact,near=near,public_references=cited,
            development_term_flags=topical,rank_key=order("issue",ident)[0]))
    save(SCRATCH,dict(upstream=upstream,projection_columns=COLUMNS,pyarrow=pa.__version__,
                      development_sources=sources,records=records))


def review_order(records):
    queues = collections.defaultdict(list)
    for row in records:
        if row["gate"] == "needs_review":
            queues[row["repo"]].append(row)
    for queue in queues.values():
        queue.sort(key=lambda r: order("issue",r["instance_id"]))
    return queues, sorted(queues,key=lambda repo:order("repo",repo))


def freeze(dest, decisions):
    doc = read(SCRATCH)
    reviews = read(decisions)
    records = doc["records"]
    by_id = {r["instance_id"]:r for r in records}
    queues, repos = review_order(records)
    used = set(); selected = []; groups = set(); visited = []
    positions = collections.Counter()
    while len(selected)<48 and any(positions[repo]<len(queues[repo]) for repo in repos):
        for repo in repos:
            while positions[repo]<len(queues[repo]):
                r = queues[repo][positions[repo]]; positions[repo]+=1
                ident=r["instance_id"]; decision=reviews.get(ident)
                need(decision and decision.get("reason"), "Missing review for "+ident)
                used.add(ident); visited.append(ident)
                if decision["decision"]=="exclude":continue
                need(decision["decision"]=="accept" and decision["group"] not in groups,ident)
                need(not any(k in {s["instance_id"] for s in selected} for k in r["exact"]), "Duplicate final prompt")
                groups.add(decision["group"]);selected.append(r);break
            if len(selected)==48:break
    need(used==set(reviews),"Review file includes candidates beyond cutoff")
    ledger=[]
    for r in records:
        ident=r["instance_id"]
        entry={k:v for k,v in r.items() if k!="prompt"}
        entry["screen"]=reviews.get(ident,{"decision":r["gate"] if r["gate"]!="needs_review" else "unvisited_after_cutoff"})
        ledger.append(entry)
    msgs=[{"id":r["instance_id"]+":issue","prompt":r["prompt"]} for r in selected]
    tasks=[]
    for i,r in enumerate(selected,1):
        ident=r["instance_id"]
        tasks.append(dict(position=i,group_id=reviews[ident]["group"],initial_message_id=ident+":issue",
                          **{k:r[k] for k in ("instance_id","repo","base_commit","environment_setup_commit",
                          "image","version","prompt_sha256","utf8_bytes","formatted_tokens")}))
    rule={"allowed_prefixes":[n for n in (12,24,36,48) if n<=len(selected)],"provisional_only":24,
          "decision":"Select a frozen ordered prefix using only six-issue development pilot costs and variability plus a prospectively approved reliability margin, precision criterion and spending cap. Sign and date the choice before unsealing any reserve predictions, routing summaries, coding or grading outcomes. If precision is unaffordable, report exploratory results.",
          "identical_routes":"Retain every assigned group including identical routes. No enrichment by classifier disagreement.",
          "denominator":"Account for all assigned/attempted groups and all arms. Retain incorrect patches, timeouts, exhausted budgets and grading failures. Record infrastructure failures separately; count every attempt and cost. No selective replacement. Preregister any infrastructure retry rule, cap, and paired analysis before paid execution.",
          "blinding":"Cache program and blind integrity reader may process results mechanically. Keep prediction reports, raw logs and comparisons sealed from sampling, scenario authoring, sample-size decisions and Mac debugging. Use only coverage and hash receipts until decisions locked."}
    save(dest/"sample-rule.json",rule)
    save(dest/"initial-prompts.json",msgs)
    save(dest/"screening-ledger.json",dict(salt=SALT,repo_order=repos,visit_order=visited,
         inclusion="Existing defect/repair in Python; leave original text intact. Screen prompt-only. Ambiguous eligibility or shared defect is grounds for exclusion.",development_sources=doc["development_sources"],rows=ledger))
    save(dest/"reserve.json",dict(schema="final-reserve-v1",upstream=doc["upstream"],
         projected_columns=COLUMNS,pyarrow=doc["pyarrow"],salt=SALT,
         ordering="Ascending SHA256 UTF-8 salt|repo|repo and salt|issue|instance_id, ID tie break. Each repository contributes its next accepted group per round until exhausted.",
         grouping="Exact normalized text, four-token shingle overlap, explicit public references, rare development terms and manual semantic review against project development topics and accepted groups. Agent-reviewed from public statements; latent relations can remain.",
         project_git=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
         selector_sha256=sha(Path(__file__)),decisions_sha256=sha(decisions),upstream_projection_fingerprint=fingerprint([{k:r[k] for k in COLUMNS if k!="problem_statement"}|{"problem_statement":r["prompt"]} for r in records]),
         source_pilot_sha256=sha(PILOT),initial_file_sha256=sha(dest/"initial-prompts.json"),
         inputs_fingerprint=fingerprint(msgs),sample_rule_sha256=sha(dest/"sample-rule.json"),ledger_sha256=sha(dest/"screening-ledger.json"),
         tasks=tasks))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=["prepare","freeze"])
    parser.add_argument("--dest",type=Path,default=DEFAULT)
    parser.add_argument("--decisions",type=Path,default=DEFAULT/"screening-decisions.json")
    args=parser.parse_args()
    if args.stage=="prepare": prepare()
    else: freeze(args.dest,args.decisions)


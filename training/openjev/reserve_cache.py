"""Run the original CUDA cache command privately. Verify coverage on Windows or Mac without inference."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/final-reserve-v1"
STUDY = ROOT / "runs/openjev/study-1"
WORK = ROOT / "runs/openjev/final-reserve-cache-v1"
VERIFY = WORK / "verification"
PINS = {"archive":"aac19a92a0525c5d356de50d543964da29ca73c312c266e9abd7ea005f44fc2e",
        "contract":"a9b11955cc79da976c3bea648ca220d7c0bc62b93de2ec1299816f510c324ee5",
        "freeze":"038cdeb7f85e967a949c7089220d8221b7931d10ce9b3e15aa8028fcac895349",
        "baseline":"58f0ff6e5cf6e73b9c46f07f9dd8237e1d72a78b0e3af71699875ae5d529389b"}


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(value,f,indent=2,allow_nan=False)
        f.write("\n")


def check(ok,message):
    if not ok: raise ValueError(message)


def init():
    original=STUDY.parent/"study-1-handoff.zip"
    check(sha(original)==PINS["archive"],"Original archive hash")
    files={"contract.json":PINS["contract"],"freeze.json":PINS["freeze"],"base-development.json":PINS["baseline"]}
    freeze=read(STUDY/"freeze.json")
    check(freeze["epoch"]==2 and freeze["contract"]==PINS["contract"],"Epoch binding")
    files.update({"epoch-2/"+f:d for f,d in freeze["adapter"].items()})
    import zipfile
    with zipfile.ZipFile(original) as z:
        files["git.json"]=hashlib.sha256(z.read("runs/openjev/study-1/git.json")).hexdigest()
    for p,d in files.items(): check(sha(STUDY/p)==d,p)
    WORK.mkdir(exist_ok=False)
    for p,d in files.items():
        dest=WORK/p; dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(STUDY/p,dest)
        check(sha(dest)==d,p)
    save(VERIFY/"original-binding.json",dict(pins=PINS,copied_files=files))


def packet(batch):
    from flash import Readout
    reader=Readout(); path=DATA/(batch+"-prompts.json")
    rows=read(path); key="reserve.json" if batch=="initial" else "scenarios.json"
    binding=read(DATA/key)
    check(sha(path)==binding[batch+"_file_sha256"] and fingerprint(rows)==binding["inputs_fingerprint"],"Message freeze")
    check(sha(DATA/"sample-rule.json")==read(DATA/"reserve.json")["sample_rule_sha256"],"Sample rule freeze")
    check(sha(WORK/"contract.json")==PINS["contract"] and sha(WORK/"freeze.json")==PINS["freeze"],"Study binding")
    check({k:list(v) for k,v in reader.choices.items()}==read(WORK/"contract.json")["choice_order"],"Candidate order")
    check(reader.letters==[32,33,34,35],"Candidate token IDs")
    check(len(rows)==len({r["id"] for r in rows}) and rows,"Unique messages")
    meta=[]
    for row in rows:
        check(set(row)=={"id","prompt"},"Input boundary")
        fields={}
        for f in reader.choices:
            ids=reader.encode(row["prompt"],f)
            fields[f]={"tokens":len(ids),"formatted_ids_sha256":fingerprint(ids)}
        meta.append(dict(id=row["id"],prompt_sha256=hashlib.sha256(row["prompt"].encode()).hexdigest(),fields=fields))
    return dict(manifest_sha256=sha(path),inputs_fingerprint=fingerprint(rows),definition_sha256=sha(DATA/key),
                sample_rule_sha256=sha(DATA/"sample-rule.json"),candidate_tokens=reader.letters,rows=meta)


def preflight(batch):
    pre=packet(batch)
    prepath=VERIFY/(batch+"-input-check.json")
    if prepath.exists(): check(read(prepath)==pre,"Preflight changed")
    else: save(prepath,pre)


def run(batch):
    # Release the tokenizer/Transformers process before Windows maps the 9B shards.
    subprocess.run([sys.executable,"-B",__file__,"preflight",batch],check=True)
    pre=read(VERIFY/(batch+"-input-check.json"))
    cache=WORK/"cached-prompts"/pre["inputs_fingerprint"]
    if cache.exists():
        previous=sorted(VERIFY.glob(batch+"-*-process.json"))
        check(previous and read(previous[-1])["returncode"]!=0 and not (cache/"comparison.json").exists(),"Existing cache cannot be retried")
        dest=WORK/"failed-attempts"/(batch+"-"+read(previous[-1])["attempt"])/cache.name
        check(cache.resolve().parent==(WORK/"cached-prompts").resolve() and dest.resolve().is_relative_to((WORK/"failed-attempts").resolve()) and not dest.exists(),"Invalid attempt paths")
        dest.parent.mkdir(parents=True,exist_ok=False)
        cache.rename(dest)
    logs=WORK/"sealed-logs";logs.mkdir(exist_ok=True)
    attempt=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    prefix=batch+"-"+attempt
    start=time.perf_counter()
    samples=[];cmd=[sys.executable,"-B","-u",str(ROOT/"training/openjev/experiment.py"),"cache-prompts","--run",str(WORK),"--prompts",str(DATA/(batch+"-prompts.json"))]
    with (logs/(prefix+".stdout")).open("xb") as out,(logs/(prefix+".stderr")).open("xb") as err:
        job=subprocess.Popen(cmd,stdout=out,stderr=err,cwd=ROOT)
        while job.poll() is None:
            try:
                q=subprocess.run(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],capture_output=True,text=True,timeout=4)
                if q.returncode==0: samples.append([round(time.perf_counter()-start,4),int(q.stdout.splitlines()[0])])
            except (OSError,ValueError,IndexError,subprocess.TimeoutExpired): pass
            try: job.wait(timeout=1.5)
            except subprocess.TimeoutExpired: pass
    perf=dict(stage="cache-prompts",batch=batch,attempt=attempt,returncode=job.returncode,
              seconds=time.perf_counter()-start,execution_order=["untuned","same loaded parent with frozen adapter"],
              utc_start=attempt,device_memory_used_MiB_samples=samples,
              memory_scope="Whole device sampled by nvidia-smi. PyTorch allocated/reserved and peak between samples unavailable.",
              model_load="Progress display in sealed stderr when emitted. No dedicated model or adapter load timer.",
              environment=read(WORK/"contract.json")["environment"])
    save(VERIFY/(prefix+"-process.json"),perf)
    check(job.returncode==0,"Cache process failed; logs retained privately.")
    verify(batch,record=True)


def verify(batch,record=False):
    pre=read(VERIFY/(batch+"-input-check.json"))
    manifest=DATA/(batch+"-prompts.json"); rows=read(manifest)
    definition=DATA/("reserve.json" if batch=="initial" else "scenarios.json")
    check(sha(manifest)==pre["manifest_sha256"]==read(definition)[batch+"_file_sha256"] and sha(definition)==pre["definition_sha256"],"Manifest binding")
    check(sha(DATA/"sample-rule.json")==pre["sample_rule_sha256"],"Prefix rule binding")
    fp=fingerprint(rows); cache=WORK/"cached-prompts"/fp
    check(read(cache/"inputs.json")=={"rows_sha256":fp,"freeze_sha256":PINS["freeze"]} and fp==pre["inputs_fingerprint"],"Input/freeze binding")
    check(read(VERIFY/"original-binding.json")["pins"]==PINS,"Original archive binding")
    check(sha(STUDY/"contract.json")==PINS["contract"] and sha(STUDY/"freeze.json")==PINS["freeze"],"Original contract/freeze")
    opts=read(STUDY/"contract.json")["choice_order"]
    check(pre["candidate_tokens"]==[32,33,34,35] and len({r["id"] for r in rows})==len(rows),"Candidate order/IDs")
    check(len(pre["rows"])==len(rows) and read(cache/"comparison.json")["n"]==len(rows),"Coverage")
    times={}
    for variant in ("base","tuned"):
        saved=read(cache/(variant+".json"))["rows"]; timing=[]
        for r,expected,s in zip(rows,pre["rows"],saved,strict=True):
            check(s["status"]=="ok" and r["id"]==s["id"]==expected["id"] and s["expected"] is None,"Row identity/status")
            check(hashlib.sha256(r["prompt"].encode()).hexdigest()==s["prompt_sha256"]==expected["prompt_sha256"],"Prompt bytes")
            check(list(s["fields"])==list(opts),"Field order")
            for f,choices in opts.items():
                d=s["fields"][f]; ref=expected["fields"][f]
                check(d["tokens"]==ref["tokens"]<=512 and d["formatted_ids_sha256"]==ref["formatted_ids_sha256"],"Formatted input")
                l,p=d["logits"],d["probabilities"]
                check(len(l)==len(p)==len(choices) and all(math.isfinite(v) for v in l+p),"Option vector")
                check(s["predicted"][f]==choices[l.index(max(l))],"Candidate slot mismatch")
                ex=[math.exp((v-max(l))/1.07) for v in l]
                check(all(abs(a/sum(ex)-b)<1e-6 and 0<=b<=1 for a,b in zip(ex,p)),"Candidate normalization")
            timing.append(s["elapsed_seconds"])
        times[variant]={"sum_row_seconds":sum(timing),"median_row_seconds":statistics.median(timing),"rows":len(timing)}
    report={"batch":batch,"passed":True,"messages_per_variant":len(rows),"decisions_per_variant":len(rows)*len(opts),
            "fingerprint":fp,"input_check_sha256":sha(VERIFY/(batch+"-input-check.json")),
            "freeze_sha256":PINS["freeze"],"contract_sha256":PINS["contract"],
            "cache_file_sha256":{p:sha(cache/p) for p in ["inputs.json","base.json","tuned.json","comparison.json"]}}
    rp=VERIFY/(batch+"-blind-verification.json")
    if record:
        save(rp,report);save(VERIFY/(batch+"-timing.json"),times)
    else:check(read(rp)==report,"Published blind receipt")
    print(json.dumps(report))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["init","preflight","run","verify"])
    parser.add_argument("batch",choices=["initial","followup"],nargs="?")
    args=parser.parse_args()
    if args.command=="init":init()
    elif args.command=="preflight":preflight(args.batch)
    elif args.command=="run":run(args.batch)
    else:verify(args.batch)


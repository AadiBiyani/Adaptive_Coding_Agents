"""Package or check the private supplement using stdlib. Never display classifier outputs."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import re
import tempfile
import zipfile
import subprocess
import sys
from reserve_cache import ROOT, DATA, STUDY, WORK, VERIFY, PINS, sha, read, save, check, verify

BASEZIP = STUDY.parent / "study-1-handoff.zip"
SUPPLEMENT = STUDY.parent / "study-1-final-reserve-v1-supplement.zip"
INDEX = "handoff-final-v1/SHA256SUMS"
BATCHES = ("initial","followup")
SOURCES = ["training/openjev/reserve_select.py","training/openjev/reserve_cache.py",
           "training/openjev/reserve_scenarios.py","training/openjev/reserve_replay.py",
           "training/openjev/reserve_handoff.py","docs/final-reserve-handoff.md"]
FROZEN = ["screening-decisions.json","screening-ledger.json","sample-rule.json","reserve.json","initial-prompts.json",
          "scenario-specs.json","scenarios.json","followup-prompts.json"]
SECRET = [
    rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----",
    rb"\b(?:sk-(?:(?:proj|svcacct|admin)-)?[a-zA-Z0-9_-]{22,}|hf_[A-Za-z0-9]{26,}|gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{35,}|(?:AKIA|ASIA)[A-Z0-9]{16}|xox[baprs]-[0-9A-Za-z-]{20,})\b",
    rb"""(?i)(?:OPENAI_API_KEY|TYPESAFE_API_KEY|AWS_SECRET_ACCESS_KEY|HF_TOKEN|CLIENT_SECRET|ACCESS_TOKEN|api[_-]?key)["']?\s*[:=]\s*["']?[a-z0-9+/.=_-]{18,}""",
    rb"(?i)\bBearer\s+[a-z0-9+/_.=-]{24,}",
    rb"(?i)https?://[A-Za-z0-9_.-]{2,}:[A-Za-z0-9!$%*_.-]{6,}@",
]


def inspect(name,raw):
    p=PurePosixPath(name)
    check(not p.is_absolute() and "\\" not in name and ":" not in name and ".." not in p.parts,"Unsafe member path")
    check(not {".git",".ssh",".aws",".cache",".venv","node_modules","__pycache__","credentials","secrets"}.intersection(p.parts)
          and not p.name.startswith(".env") and p.suffix not in {".key",".pem",".p12",".pfx",".sqlite",".pyc"},"Unexpected private configuration")
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as nested:
            check(nested.testzip() is None,"Nested ZIP integrity")
            for i in nested.infolist():
                if not i.is_dir():inspect(i.filename,nested.read(i))
    else:
        check(all(not re.search(rule,raw) for rule in SECRET),"Potential credential in "+name)


def archive_inventory(path,index):
    with zipfile.ZipFile(path) as z:
        check(z.testzip() is None,"ZIP CRC failure")
        lines=z.read(index).decode("utf-8").splitlines()
        expected={name:dig for dig,name in (line.split("  ",1) for line in lines)}
        check(len(z.infolist())==len(lines)+1==len(expected)+1 and set(z.namelist())==set(expected)|{index},"ZIP membership")
        for name,dig in expected.items():
            b=z.read(name);check(hashlib.sha256(b).hexdigest()==dig,"ZIP payload integrity")
            if index==INDEX:inspect(name,b)
    return expected


def bound_inputs():
    check(sha(BASEZIP)==PINS["archive"],"Original ZIP digest")
    old=archive_inventory(BASEZIP,"handoff/SHA256SUMS")
    for name,dig in old.items():
        if name.startswith(("runs/openjev/study-1/","training/openjev/","backend/src/","data/","runs/openjev/environment-study-1/","runs/openjev/smoke-")):
            check(sha(ROOT/name)==dig,"Historical artifact changed: "+name)
    return old


def verify_bindings():
    binding=read(VERIFY/"original-binding.json")
    check(binding["pins"]==PINS,"Study pins")
    for name,checksum in binding["copied_files"].items():
        check(sha(STUDY/name)==sha(WORK/name)==checksum,"Original and working file: "+name)
    for name,checksum in read(STUDY/"contract.json")["code_hashes"].items():
        source=ROOT/"training/openjev"/name
        if not source.is_file():source=ROOT/"backend/src/adaptive_coding_agents"/name
        check(sha(source)==checksum,"Contract source: "+name)
    reserve=read(DATA/"reserve.json")
    scenarios=read(DATA/"scenarios.json")
    replay=read(VERIFY/"selection-replay.json")
    check(replay["passed"] and sha(ROOT/SOURCES[0])==reserve["selector_sha256"],"Reserve replay binding")
    check(len(reserve["tasks"])==len({t["group_id"] for t in reserve["tasks"]})==replay["selected_issues"],"Reserved groups")
    for name,checksum in replay["matching_file_sha256"].items():check(sha(DATA/name)==checksum,"Frozen selection file")
    check(sha(DATA/"screening-decisions.json")==reserve["decisions_sha256"],"Screening decision source")
    check(sha(DATA/"scenario-specs.json")==scenarios["authoring_spec_sha256"] and
          sha(ROOT/"training/openjev/reserve_scenarios.py")==scenarios["builder_sha256"],"Scenario authoring source")
    lengths={t["initial_message_id"]:t["formatted_tokens"] for t in reserve["tasks"]}
    for row in read(VERIFY/"initial-input-check.json")["rows"]:
        check(lengths[row["id"]]=={f:x["tokens"] for f,x in row["fields"].items()},"Selection/scoring lengths")
    return binding


def build():
    old=bound_inputs()
    binding=verify_bindings()
    for b in BATCHES: verify(b)
    payload=[DATA/name for name in FROZEN]+[ROOT/p for p in SOURCES]+[VERIFY/"original-binding.json",VERIFY/"selection-replay.json"]
    payload.extend(WORK/name for name in binding["copied_files"])
    for b in BATCHES:
        receipt=read(VERIFY/(b+"-blind-verification.json"))
        cache=WORK/"cached-prompts"/receipt["fingerprint"]
        payload.extend(cache/n for n in ("base.json","tuned.json","comparison.json","inputs.json"))
        payload.extend(VERIFY/(b+n) for n in ("-input-check.json","-blind-verification.json","-timing.json"))
        for proc in sorted(VERIFY.glob(b+"-*-process.json")):
            payload.append(proc)
            prefix=b+"-"+read(proc)["attempt"]
            payload.extend(WORK/"sealed-logs"/(prefix+suffix) for suffix in (".stdout",".stderr"))
            failed=WORK/"failed-attempts"/prefix/receipt["fingerprint"]
            for name in ("inputs.json","base.json","tuned.json","comparison.json"):
                if (failed/name).is_file():payload.append(failed/name)
    provenance={"original_archive_sha256":PINS["archive"],"contract_sha256":PINS["contract"],"freeze_sha256":PINS["freeze"],
        "git_base":read(STUDY/"git.json")["revision"],"new_source_sha256":{n:sha(ROOT/n) for n in SOURCES},
        "selected_epoch":2,"original_payload_count_verified":len(old),"source_identity":"Working file SHA-256 values identify the new tooling, independent of commit status.",
        "public_check_execution":"Compiled only. No task code or grader executed.","blinding":"Private storage and procedural blinding. Only the integrity receipt should be opened before selection is locked."}
    extra={"handoff-final-v1/binding.json":(json.dumps(provenance,indent=2)+"\n").encode()}
    wanted={p.relative_to(ROOT).as_posix():p for p in payload}
    check(len(payload)==len(wanted) and not set(wanted)&set(old),"Supplement collision")
    check(not SUPPLEMENT.exists() and not SUPPLEMENT.with_suffix(".zip.sha256").exists(),"Supplement output exists")
    members={n:p.read_bytes() for n,p in wanted.items()};members.update(extra)
    for n,b in members.items():inspect(n,b)
    members[INDEX]="".join(f"{hashlib.sha256(b).hexdigest()}  {n}\n" for n,b in sorted(members.items())).encode()
    # Build and inspect a private temporary ZIP before publishing under its final name.
    tmp=SUPPLEMENT.with_suffix(".partial.zip")
    with zipfile.ZipFile(tmp,"x",zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(members.items()):z.writestr(n,b)
    archive_inventory(tmp,INDEX)
    # Exclusive publication, including on platforms where rename can replace files.
    with SUPPLEMENT.open("xb") as dest,tmp.open("rb") as source:
        import shutil
        shutil.copyfileobj(source,dest)
    check(sha(tmp)==sha(SUPPLEMENT),"Publication checksum")
    tmp.unlink()
    signature=sha(SUPPLEMENT)
    with SUPPLEMENT.with_suffix(".zip.sha256").open("x",encoding="ascii",newline="\n") as f:
        f.write(signature+"  "+SUPPLEMENT.name+"\n")
    print("Supplement bytes",SUPPLEMENT.stat().st_size,"SHA-256",signature,"members",len(members))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("action",choices=("build","verify-restored"))
    args=parser.parse_args()
    if args.action=="build":build()
    else:
        for index in ("handoff/SHA256SUMS",INDEX):
            for line in (ROOT/index).read_text(encoding="utf-8").splitlines():
                dig,n=line.split("  ",1);check(sha(ROOT/n)==dig,"Restored payload mismatch: "+n)
        b=read(ROOT/"handoff-final-v1/binding.json")
        check((b["original_archive_sha256"],b["contract_sha256"],b["freeze_sha256"])==
              (PINS["archive"],PINS["contract"],PINS["freeze"]),"Cross-archive binding")
        verify_bindings()
        for batch in BATCHES:verify(batch)
        print("Restored payload and blind cache checks passed.")


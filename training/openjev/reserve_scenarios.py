"""Materialize the reviewed visible branch specs. Compile the public probes without executing task code."""
import argparse
from pathlib import Path

from reserve_select import DEFAULT, ROOT, read, save, sha, digest, fingerprint, need


def freeze_scenarios(dest):
    reserve=read(dest/"reserve.json")
    receipt=ROOT/"runs/openjev/final-reserve-cache-v1/verification/initial-blind-verification.json"
    need(read(receipt)["passed"] and read(receipt)["fingerprint"]==reserve["inputs_fingerprint"],"Initial coverage required")
    specs=read(dest/"scenario-specs.json")
    messages=[];scenarios=[];ledger=[];repos=set()
    for t in reserve["tasks"]:
        i=t["instance_id"]
        if t["repo"] in repos:
            ledger.append(dict(instance_id=i,decision="skip",reason="Earlier selected group represents this repository."));continue
        need(i in specs,"Missing scenario screening decision for "+i)
        s=specs[i]
        if "skip" in s:
            ledger.append(dict(instance_id=i,decision="skip",reason=s["skip"]));continue
        code=s["public_check"]
        compile(code,i+"-public-check.py","exec",dont_inherit=True)
        ids={}
        for kind in ("required","corrective"):
            msg_id=i+":"+kind;messages.append({"id":msg_id,"prompt":s[kind]});ids[kind+"_id"]=msg_id
        scenarios.append(dict(instance_id=i,group_id=t["group_id"],base_commit=t["base_commit"],
                         initial_id=t["initial_message_id"],**ids,**s,public_check_sha256=digest(code)))
        ledger.append(dict(instance_id=i,decision="select",reason=s["motivation"]))
        repos.add(t["repo"])
        if len(scenarios)==6:break
    need(len(repos)==6 and len({x["id"] for x in messages})==12,"Distinct groups/messages")
    need(set(specs)=={s["instance_id"] for s in ledger if s["instance_id"] in specs},"Extraneous specs")
    save(dest/"followup-prompts.json",messages)
    save(dest/"scenarios.json",dict(schema="final-controlled-scenarios-1",selection="Earliest eligible distinct repositories in frozen reserve order.",
        eligibility="An additional visible requirement and self-contained executable public probe can be specified from the public functional report.",
        designed_using="Frozen initial statements and public behavior. Selection and design excluded all classifier predictions, hidden checks, reference patches and later coding outcomes.",
        initial_manifest_sha256=sha(dest/"initial-prompts.json"),reserve_sha256=sha(dest/"reserve.json"),
        authoring_spec_sha256=sha(dest/"scenario-specs.json"),builder_sha256=sha(Path(__file__)),
        followup_file_sha256=sha(dest/"followup-prompts.json"),inputs_fingerprint=fingerprint(messages),
        screening=ledger,scenarios=scenarios,maximum_user_turns=3,
        control={"start":"Fresh isolated workspace and coding session per strategy/scenario. Standard and controlled runs are separate trajectories. Send the exact existing initial message.",
                 "after_initial":"Following a completed first coding turn deliver the mandatory follow-up even when the agent declares success.",
                 "after_required":"Run the public Python probe with asserts enabled in the pinned environment. Pass stops the conversation. Assertion failure or exception attributable to candidate code triggers the exact corrective message once.",
                 "after_corrective":"Repeat the same probe, record its outcome and stop. Never issue a fourth message.",
                 "terminal":"Record budget, timeout, provider or infrastructure stops with all incurred costs. Missing dependencies or unusable environment are infrastructure outcomes. Do not use them to trigger a corrective hint.",
                 "grading":"From clean base regrade final patch with the independent original SWE-bench grader. Record original resolution, public additional requirement, any regression and their conjunction. Preserve results on all attempted tasks.",
                 "visibility":"Keep future messages, controller, archived caches and hidden grader outside the coding workspace. Only exact current prompt reaches the classifier.",
                 "validation":"All six probes compiled on Windows. No public probe, task checkout, patch, or hidden grader was executed. Exercise public probes in isolated pinned task environments under a predeclared protocol before paid evaluation."}))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--dest",type=Path,default=DEFAULT)
    freeze_scenarios(parser.parse_args().dest)


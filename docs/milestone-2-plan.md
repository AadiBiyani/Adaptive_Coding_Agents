# Milestone 2 deliverables and 10-day plan

**Inactive course reference as of October 24, 2026.** The owner explicitly set Milestone 2 aside to resolve the full product and research design. Follow [Development plan](development-plan.md) for active work. The requirements and historical ten-day proposal below are retained for later course use; they do not authorize implementation, spending, scheduling, or submissions now. Recheck the course package and deadline if this work is resumed.

Prepared October 24, 2026 from the supplied course announcement and the official ai-product-milestone-2-package.zip already downloaded locally. The package README and requirements.json were read in full, along with the brief, real-path submission template, and review guides. This is a planning document; no prototype, review, result, or final submission is claimed complete.

## What this milestone requires

Milestone 2 is the preliminary product and stakeholder review. The package permits a working prototype **or preliminary result**, accompanied by usable instructions, an updated brief, structured submission records, and real-stakeholder evidence. It does not specify completion of the entire project's fine-tuning or benchmark study.

We are using the established real-stakeholder path. The 15-minute presentation video and three virtual-persona reviews apply to the virtual path, not this submission. The real-path review is about 30 minutes, including presentation/demonstration, questions, and feedback. Slides are optional.

The existing development repository still contains documentation only. The prior milestone's agreement/validation evidence remains in the private course workspace; no new review or feedback has been supplied.

## Required deliverables

| Deliverable | What we need to produce or carry forward | Requirement |
| --- | --- | --- |
| Prototype or preliminary result | Substantive product work under supporting/, logged with kind prototype. Include code/configuration and/or genuine measured results. A plan alone is not our proposed submission. | REQ-M2-01 |
| Prototype README | supporting/prototype/README.md: what exists, setup/run/use instructions, example walkthroughs, expected output, and current limitations. Log as prototype_readme and point prototype.readme_file to it. | REQ-M2-01 |
| Updated brief.md | Root brief with exactly Product value case and Engineering credibility checks as its two H2 headings. Explain current capabilities, evidence, consequential feedback, uncertainties, lessons, and resulting decisions/tests. Integrate feedback into those sections. | REQ-M2-01, REQ-C03 |
| Review session documentation | Hold the approximately 30-minute review and provide a full audio/video recording, a detailed written summary, or both. A summary may be Markdown or PDF. Include date/duration/attendees, what was shown, substantive questions/responses, and feedback. | REQ-M2-R02; package README |
| Stakeholder-authored feedback PDF | A feedback email written by the stakeholder and saved as PDF, or a PDF they signed. It must discuss the product/review. This is separate from the session summary/recording and the original consent email. | REQ-M2-R01 |
| Agreement and validation evidence | Carry forward the applicable agreement, approval-email PDF, personal-email consent audio, and exact stakeholder-facing brief evidence. Keep the reviewed material/version identifiable; retain the old approved brief if a newer version is shared. | REQ-R01–R03 |
| Completed submission.yaml | Milestone 2, real path, correct student/product/stakeholder data, artifact/evidence pointers, all manifests, intake decisions, and four truthful attestations personally confirmed for this final submission. | REQ-C01–C08 |
| Validated final ZIP and upload check | Package only the declared files, inspect and validate the exact ZIP, upload to Gradescope, and check/fix its format report before the deadline. Structural validity does not establish product quality or factual accuracy. | Package README and supplied announcement |

Recordings are optional for our path. If recording, ask permission before starting; the old stakeholder agreement is not recording permission. Submit one full recording of at most 100 MB (104,857,600 bytes), without splitting it or substituting a link. The existing short consent audio serves identity/validation and does not document the new review.

A detailed summary is allowed without a special waiver or explanation. The package explicitly retired REQ-M2-R03 on October 22. The stakeholder's own feedback PDF is required even when a full recording or summary is submitted.

A separate feedback-synthesis.md, slide PDF, numeric stakeholder ratings, and the suggested feedback rubric are not required for this milestone's real path. Some generic package text mentions a synthesis file “when required”; its Milestone 2 instructions place the synthesis inside brief.md.

## Proposed product scope for these 10 days

This is a recommended milestone target, not an additional course requirement or a measured result. Preserve the full research scope in [Development plan](development-plan.md).

Aim to demonstrate a new prompt entering a dedicated terminal command, a hosted Jev decision selecting a supported GPT configuration, and a coding turn that uses the chosen model/effort. Show at least one follow-up retaining session/repository context. Start with around two eligible GPT models and a few verified configurations, a fixed fallback, and logs for decisions, usage, cost, latency, and failures. Exact choices and spending caps remain open.

For preliminary evidence, target a tiny, pinned development SWE-bench subset comparing a fixed configuration with hosted-Jev routing under matched conditions. Three to five tasks is a planning suggestion subject to actual setup cost and authorized budget, not a statistically conclusive study or required task count. Preserve patches and executable evaluator outcomes; explain failures and uncertainty. Add one controlled multi-turn walkthrough to demonstrate continuity, without claiming it proves fewer human prompts.

This gives the stakeholder something concrete to review: the terminal interaction, routing choices, working/failing bug-fix examples, and preliminary cost/time evidence.

Fine-tuned OpenJev, the full hosted/untuned/tuned comparison, and the larger held-out evaluation remain project deliverables. The course package does not explicitly require them for Milestone 2. Plan them after a stable preliminary demo and review; if an affordable training smoke test fits, treat it as extra progress rather than risking the required evidence and submission.

If the integration blocks progress by Day 3, assess an honest preliminary-result submission based on verified experiments with documented integration limitations. Do not fabricate a working router. Preserve time for the stakeholder review even when the prototype is incomplete.

## Ten-day schedule

Days are relative to the owner's stated ten-day window. The precise calendar deadline/time has not been independently confirmed. This schedule is proposed, not execution authorization.

| Day | Work | Completion checkpoint |
| --- | --- | --- |
| 1 | Set the milestone scope, budget limits, runtime/interface, and task shortlist. Arrange the stakeholder review for Day 7, with Day 8 available as backup. Read the package before preparing a separate private submission workspace. | Small implementation target, budget decisions for paid work, review invitation sent by the owner, and clear evidence checklist. |
| 2–3 | Once authorized, build the minimal terminal/session path with fixed/stub configuration; prove follow-up continuity and settings with a bounded live check. | A real two-turn workflow, or a documented integration issue with a revised preliminary-result plan. |
| 4–5 | Add hosted Jev, registry validation, fallback, spending stops, and usage/decision records. | Demonstrable per-prompt routing with traceable settings and failures. |
| 6 | Run the small authorized development benchmark comparison; save patches/results and prepare the walkthrough. Draft prototype instructions and current-state brief. | An honest preliminary results table and a stable review demo. |
| 7 | Conduct the approximately 30-minute stakeholder review. Take detailed notes; record only with permission. Request their own feedback email or signed PDF. | Actual review completed and summary drafted promptly; written feedback requested. |
| 8 | Obtain feedback PDF, address priority issues within scope, and revise the brief with feedback, lessons, and decisions. Record any post-review prototype changes. | Feedback evidence received and traceable to the version reviewed. |
| 9 | Assemble the private package; carry forward validation records; log every file; verify README/run instructions; resolve checker findings. | Complete draft submission for the owner's factual review. |
| 10 | Personally confirm final attestations, package/inspect/validate the exact ZIP, upload, and review Gradescope's format report. Leave time to correct and resubmit. | Final uploaded package with checked format report. |

Do not wait until the final day to obtain stakeholder feedback. Scheduling and evidence collection are dependencies alongside implementation. No messages have been sent or meetings booked by the agent.

## Package assembly checklist

Keep the private submission package separate from the public development repository. This planning document contains no stakeholder contact or validation records.

- [ ] Substantive prototype/result files under supporting/, each declared in supporting_artifacts.
- [ ] supporting/prototype/README.md included, declared, and named in prototype.readme_file.
- [ ] Current root brief.md has the two exact headings, accurate prototype claims, and integrated feedback/decisions.
- [ ] Applicable agreement PDF, approval-email PDF, consent audio, and exact stakeholder-facing brief under evidence/real/RS-01/.
- [ ] Full review recording and/or detailed review-session summary, with matching review_session pointers.
- [ ] Separate stakeholder-feedback.pdf with source_method email or signed_pdf.
- [ ] Every evidence file listed exactly once in evidence_manifest; all intake files have explicit decisions.
- [ ] Structured fields match source evidence; optional ratings remain null unless actually supplied.
- [ ] Student confirms the four attestations for the completed Milestone 2 submission; no placeholders remain.
- [ ] guide_submission.py status findings resolved, package_submission.py validates the exact final ZIP, and the owner inspects it.
- [ ] Gradescope upload and its format report checked before the actual deadline.

When assembling, follow the package's own AGENTS.md and use its supplied tools unmodified. Those packaging rules apply to the private submission workspace; they do not replace development instructions here.

## Formal requirement text

The following quotations are copied from the inspected package's requirements.json. The README adds the approximate 30-minute review expectation and procedural instructions. REQ-R04 concerns shared agreements and is not part of our current individual arrangement. Virtual-path requirements do not apply.

### REQ-M2-01

> Milestone 2 must include the current brief, which integrates the most consequential stakeholder feedback, what was learned, and the resulting decisions or tests under its two required headings, and the preliminary product: at least one supporting artifact of kind prototype plus a prototype README, named in prototype.readme_file and listed as an included supporting artifact, that explains what the prototype is, how to run or use it, what to try, and its limitations.

### REQ-M2-R01

> Each real stakeholder must provide feedback on the product or review in their own email, saved as a PDF, or in a PDF they signed; consent alone does not qualify, a student-written summary or recording does not replace it, and any format or rubric is accepted without transcribing ratings.

### REQ-M2-R02

> Each real stakeholder's review session must be documented by its full audio or video recording, a detailed written summary, or both; a recording is encouraged with the stakeholder's permission, and any submitted recording must be one file of at most 100 MB.

### REQ-R01

> The real path must include at least one eligible non-Purdue-student stakeholder with identity, affiliation, relationship, direct interest, contact information, and the exact stakeholder-facing brief.

### REQ-R02

> Each real stakeholder must have the applicable individual or shared agreement and approval evidence; email approval requires the approval-email PDF.

### REQ-R03

> Institutional-email validation requires the institutional address; personal-email validation requires the personal address and a nonempty consent audio file in .wav, .mp3, .m4a, or .aac format.

### REQ-C01

> The final archive must contain one root submission.yaml that parses as JSON-compatible YAML with unique object keys and identifies the correct integer milestone and submission mode.

### REQ-C02

> The submission must identify the student, product title, selected stakeholder path, and primary brief.

### REQ-C03

> The AI Product Brief must use the two required headings with nonempty student-written sections, contain no active HTML or unsafe link destination, and accurately state the concise value case and engineering credibility checks.

### REQ-C04

> Every included supporting artifact must be logged in supporting_artifacts, every evidence file must be listed exactly once in evidence_manifest, and every file in the final ZIP must be accounted for.

### REQ-C05

> A final submission must contain no template placeholders and must include all four truthful student attestations, the student's name, and the attestation date.

### REQ-C06

> The structured record must accurately represent the brief, artifacts, and original evidence; this consistency and truthfulness remain subject to manual or AI-assisted review.

### REQ-C07

> Every non-instruction file placed in inbox must have an explicit intake_file_decisions record that includes it as supporting work, includes it as evidence, or ignores it with a stated reason.

### REQ-C08

> The primary brief must be brief.md at the ZIP root; when required, feedback-synthesis.md must also be at the root. Included artifacts belong under supporting/, real-stakeholder evidence under evidence/real/<stakeholder_id>/, virtual transcript and model evidence under evidence/virtual/<persona_id>/, and course prompt files under prompts/.

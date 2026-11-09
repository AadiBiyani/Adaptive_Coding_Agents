import { useEffect, useRef, useState } from "react"
import { ChevronLeft, ChevronRight, Download, LoaderCircle, Play, Square } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { api, money, shortDate } from "@/lib/api"

const label = value => value?.replaceAll("_", " ") || "—"
const percent = value => value == null ? "—" : `${(value * 100).toFixed(1)}%`

export function PilotCostPreview({ preview }) {
  return <div className="space-y-3 text-sm">
    <p>You are about to spend tokens to run {preview.planned} {label(preview.split)} prompts. Are you sure you want to run these tests?</p>
    <div className="rounded-xl border border-border p-4 leading-7">
      <p>Jev: {preview.jev_requests} requests · {money(preview.admission_estimate_usd.jev)} admission estimate</p>
      <p>OpenAI: {preview.openai_calls} calls · {money(preview.admission_estimate_usd.openai)}</p>
    </div>
    <p className="text-xs leading-5 text-muted-foreground">This tests classification only. No coding model or baseline runs. The estimate is an allowance against your existing budget, not a guaranteed bill. No automatic retries.</p>
    <p className="text-xs text-muted-foreground">Shared Jev budget remaining: {money(preview.remaining_usd.jev)} · {preview.jev_requests_remaining} requests left for this experiment. Confirmation expires after five minutes.</p>
  </div>
}

export function ClassifierResult({ run }) {
  if (!run) return null
  const report = run.report
  function download() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(run, null, 2)], { type: "application/json" }))
    const link = document.createElement("a")
    link.href = url; link.download = `classifier-${run.id}.json`; link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return <section className="space-y-4" aria-label="Classifier results">
    <div className="flex flex-wrap items-center justify-between gap-3"><h2 className="font-medium">{label(run.plan.split)} results <Badge variant="secondary" className="ml-2 font-normal">{label(run.status)}</Badge></h2><Button variant="ghost" size="sm" onClick={download} disabled={["running", "stopping"].includes(run.status)}><Download className="size-4" />Export classifier report</Button></div>
    {run.error && <p role="alert" className="text-sm text-destructive">{run.error}</p>}
    <div className="grid grid-cols-2 gap-5 rounded-xl border border-border p-5 sm:grid-cols-4">{[
      ["Prompts attempted", `${report?.metrics?.attempted ?? 0} / ${run.plan.planned}`],
      ["All labels correct", percent(report?.metrics?.all_fields_exact_match)],
      ["Provider failures", report?.metrics?.failures ?? 0],
      ["Jev cost estimate", money(report?.estimated_cost_usd)],
    ].map(([name, value]) => <div key={name}><p className="text-xs text-muted-foreground">{name}</p><p className="mt-2 text-lg tabular-nums">{value}</p></div>)}</div>
    {report?.stop_reason && <p className="text-sm text-muted-foreground">Stopped: {label(report.stop_reason)}. Unattempted: {report.unattempted}.</p>}
    {report?.metrics?.fields && <Table><TableHeader><TableRow><TableHead>Category</TableHead><TableHead>Accuracy</TableHead><TableHead>Macro-F1</TableHead></TableRow></TableHeader><TableBody>{Object.entries(report.metrics.fields).map(([key, field]) => <TableRow key={key}><TableCell>{label(key)}</TableCell><TableCell>{percent(field.accuracy)}</TableCell><TableCell>{field.macro_f1 == null ? "—" : field.macro_f1.toFixed(3)}</TableCell></TableRow>)}</TableBody></Table>}
    {!!report?.results?.length && <details className="rounded-xl border border-border"><summary className="cursor-pointer px-4 py-3 text-sm">Individual predictions and reviewed labels</summary><div className="max-h-96 overflow-auto border-t border-border"><Table><TableHeader><TableRow><TableHead>Prompt</TableHead><TableHead>Reviewed labels</TableHead><TableHead>Jev prediction</TableHead></TableRow></TableHeader><TableBody>{report.results.map(row => <TableRow key={row.id}><TableCell className="align-top text-xs">{row.id}<br /><span className="text-muted-foreground">{row.elapsed_ms == null ? "—" : `${row.elapsed_ms} ms`}</span></TableCell><TableCell className="align-top text-xs leading-6">{Object.entries(row.expected).map(([k, v]) => <p key={k}>{label(k)}: {label(v)}</p>)}</TableCell><TableCell className="align-top text-xs leading-6">{row.predicted ? Object.entries(row.predicted).map(([k, v]) => <p key={k} className={v !== row.expected[k] ? "text-destructive" : ""}>{label(k)}: {label(v)}</p>) : label(row.status)}</TableCell></TableRow>)}</TableBody></Table></div></details>}
    <p className="text-xs leading-5 text-muted-foreground">Classifier agreement on authored prompts; not coding-task success or SWE-bench performance. Failed attempts count in accuracy. Unknown usage stays unavailable. Full confusion matrices, usage, latency, and version fingerprints are included in the export.</p>
  </section>
}

export function ClassifierPilot({ codingBusy, onBudget }) {
  const [data, setData] = useState(null)
  const [split, setSplit] = useState("development")
  const [index, setIndex] = useState(0)
  const [labels, setLabels] = useState({})
  const [reviewer, setReviewer] = useState("")
  const [reviewed, setReviewed] = useState(false)
  const [freeze, setFreeze] = useState("")
  const [refresh, setRefresh] = useState(0)
  const [error, setError] = useState("")
  const [working, setWorking] = useState(false)
  const [confirmation, setConfirmation] = useState(null)
  const [selected, setSelected] = useState(null)
  const [run, setRun] = useState(null)
  const sending = useRef(false)
  const row = data?.examples[index]
  const counts = data?.counts[split]
  const busy = !!data?.active_id
  const blocked = busy || codingBusy || data?.other_busy || working
  const freezeId = freeze || data?.development_reports[0]?.id || ""
  const ready = counts?.total > 0 && counts.reviewed === counts.total && data?.credentials_ready && (split === "development" || freezeId)

  useEffect(() => {
    let disposed = false, timer
    async function poll() {
      try {
        const next = await api(`/classifier-pilot?split=${split}`)
        if (disposed) return
        setData(next); onBudget?.(next.budget)
        const id = selected || next.active_id || next.runs[0]?.id
        if (id) {
          const result = await api(`/classifier-pilot/runs/${id}`)
          if (disposed) return
          setRun(result)
        } else setRun(null)
        // Keep other-tab jobs and completed batches visible without a page reload.
        if (!disposed) timer = setTimeout(poll, next.active_id ? 800 : 4000)
      } catch (e) {
        if (!disposed) { setError(e.message); timer = setTimeout(poll, 3000) }
      }
    }
    poll()
    return () => { disposed = true; clearTimeout(timer) }
  }, [split, selected, refresh, onBudget])
  useEffect(() => { setLabels(row?.labels || {}); setReviewed(false) }, [row?.id, row?.review?.reviewed_at])

  async function act(operation) {
    if (sending.current) return
    sending.current = true; setWorking(true); setError("")
    try { await operation() }
    catch (e) { setError(e.message) }
    finally { sending.current = false; setWorking(false); setRefresh(v => v + 1) }
  }
  function save() {
    act(async () => {
      const next = await api("/classifier-pilot/annotations", { example_id: row.id, labels, reviewer_id: reviewer,
        reviewed, dataset_sha256: data.dataset_sha256 })
      setData(previous => ({ ...previous, ...next })); setReviewed(false)
      setIndex(i => Math.min(i + 1, next.examples.length - 1))
    })
  }
  function preview() {
    act(async () => {
      const result = await api("/classifier-pilot/preview", { split, freeze_id: split === "held_out" ? freezeId : null })
      setConfirmation({ ...result, request_id: crypto.randomUUID() })
    })
  }
  function start() {
    act(async () => {
      const result = await api("/classifier-pilot/runs", { request_id: confirmation.request_id,
        confirmation_token: confirmation.confirmation_token, confirmed: true })
      setSelected(result.id); setRun(result); setConfirmation(null)
    })
  }

  return <div className="space-y-7">
    <div className="space-y-4 rounded-2xl border border-border p-5">
      <div><h2 className="font-medium">40-prompt Jev classifier pilot</h2><p className="mt-2 text-sm leading-6 text-muted-foreground">20 development prompts + 20 held-out prompts. Review labels, run a split, and compare Jev’s predictions. Each prompt is classified independently; Jev never receives your reviewed labels.</p></div>
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
      {!data ? <p className="text-sm text-muted-foreground">Loading pilot…</p> : !data.available ? <div className="space-y-2 text-sm"><p>{data.error}</p><p className="text-muted-foreground">Prepare the unlabelled prompts locally with no API calls:</p><code className="block overflow-x-auto rounded-lg bg-secondary p-3 text-xs">.venv/bin/python backend/scripts/prepare_classifier_pilot.py</code></div> : <>
        <div className="flex flex-wrap items-end gap-3"><div className="min-w-48 flex-1 space-y-2"><label htmlFor="pilot-split" className="text-sm">Prompt split</label><Select value={split} onValueChange={value => { setData(null); setSplit(value); setIndex(0); setError(""); setConfirmation(null) }} disabled={working}><SelectTrigger id="pilot-split" className="w-full"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="development">Development · {data.counts.development.total}</SelectItem><SelectItem value="held_out">Held-out · {data.counts.held_out.total}</SelectItem></SelectContent></Select></div><Badge variant="secondary" className="py-2">{counts?.reviewed} / {counts?.total} labels reviewed</Badge></div>
        {row && <div className="space-y-4 border-t border-border pt-4">
          <div className="flex items-center justify-between"><p className="text-sm">Prompt {index + 1} of {data.examples.length}</p><div className="flex gap-1"><Button variant="ghost" size="icon" aria-label="Previous prompt" disabled={!index || working} onClick={() => setIndex(i => i - 1)}><ChevronLeft className="size-4" /></Button><Button variant="ghost" size="icon" aria-label="Next prompt" disabled={index + 1 >= data.examples.length || working} onClick={() => setIndex(i => i + 1)}><ChevronRight className="size-4" /></Button></div></div>
          <pre className="whitespace-pre-wrap rounded-xl bg-secondary p-4 font-mono text-sm leading-6">{row.prompt}</pre>
          <p className="text-xs leading-5 text-muted-foreground">Use only this prompt. Do not infer previous messages or inspect repository files. Choose unknown or mixed when information is absent. Related prompt pairs stay in the same split.</p>
          <div className="grid gap-4 sm:grid-cols-3">{Object.entries(data.questions).map(([name, question]) => <div key={name} className="space-y-2"><label htmlFor={`label-${name}`} className="text-sm capitalize">{label(name)}</label><Select value={labels[name] || ""} onValueChange={value => setLabels(current => ({ ...current, [name]: value }))} disabled={blocked || data.annotations_locked}><SelectTrigger id={`label-${name}`} className="w-full"><SelectValue placeholder="Choose a label" /></SelectTrigger><SelectContent>{Object.keys(question.criteria).map(value => <SelectItem key={value} value={value}>{label(value)}</SelectItem>)}</SelectContent></Select><details className="text-xs leading-5 text-muted-foreground"><summary className="cursor-pointer">Category definitions</summary>{Object.entries(question.criteria).map(([key, definition]) => <p key={key} className="mt-2"><strong>{label(key)}:</strong> {definition}</p>)}</details></div>)}</div>
          {data.annotations_locked ? <p className="text-xs text-muted-foreground">Annotations are frozen while a batch is running and after predictions exist for this split.</p> : <div className="space-y-3"><label htmlFor="pilot-reviewer" className="block text-sm">Reviewer nickname (no email needed)</label><Input id="pilot-reviewer" value={reviewer} maxLength={80} onChange={e => setReviewer(e.target.value)} placeholder="Your initials or nickname" disabled={blocked} /><label className="flex items-start gap-2 text-sm leading-5"><input type="checkbox" className="mt-1 accent-foreground" checked={reviewed} onChange={e => setReviewed(e.target.checked)} disabled={blocked} />I reviewed these labels using only the prompt shown above.</label><Button variant="outline" onClick={save} disabled={blocked || !reviewed || !reviewer.trim() || Object.keys(data.questions).some(key => !labels[key])}>Save labels & next</Button></div>}
        </div>}
        {split === "held_out" && <div className="space-y-2 border-t border-border pt-4"><label htmlFor="pilot-freeze" className="text-sm">Freeze from completed development run</label><Select value={freezeId} onValueChange={setFreeze} disabled={blocked}><SelectTrigger id="pilot-freeze" className="w-full"><SelectValue placeholder="Complete the development split first" /></SelectTrigger><SelectContent>{data.development_reports.map(item => <SelectItem key={item.id} value={item.id}>{shortDate(item.started_at)} · {item.id.slice(0, 8)}</SelectItem>)}</SelectContent></Select><p className="text-xs leading-5 text-muted-foreground">The backend verifies that the dataset, reviewed development labels, model, and questions still match. Do not tune the classifier after inspecting held-out predictions.</p></div>}
        <div className="flex flex-wrap items-center gap-3 border-t border-border pt-4">{busy ? <Button variant="outline" disabled={working} onClick={() => act(() => api(`/classifier-pilot/runs/${data.active_id}/stop`, {}))}><Square className="size-3.5" />Stop after current request</Button> : <Button onClick={preview} disabled={blocked || !ready}>{working ? <LoaderCircle className="size-4 animate-spin" /> : <Play className="size-4" />}Review cost & run Jev tests</Button>}<p className="text-xs text-muted-foreground">Only confirming starts paid requests.</p></div>
        {!data.credentials_ready && <p className="text-xs text-muted-foreground">Add your TypeSafe key to .env and restart the server to enable the live pilot.</p>}
        {(codingBusy || data.other_busy) && <p className="text-xs text-muted-foreground">Finish the active coding response or evaluation first.</p>}
      </>}
    </div>
    <ClassifierResult run={run} />
    {!!data?.runs.length && <section><h2 className="mb-3 text-sm font-medium">Classifier run history</h2><div className="divide-y divide-border">{data.runs.map(item => <Button key={item.id} variant="ghost" className="h-auto w-full justify-between rounded-none py-3 font-normal" onClick={() => setSelected(item.id)}><span>{label(item.split)} · {shortDate(item.started_at)}</span><span className="text-xs text-muted-foreground">{label(item.status)}</span></Button>)}</div></section>}
    <Dialog open={!!confirmation} onOpenChange={open => { if (!open && !working) { setConfirmation(null); setError("") } }}><DialogContent showCloseButton={!working}><DialogHeader><DialogTitle>Run paid classifier tests?</DialogTitle><DialogDescription>Review which providers will be used before you confirm.</DialogDescription></DialogHeader>{confirmation && <PilotCostPreview preview={confirmation} />}{error && <p role="alert" className="text-sm text-destructive">{error}</p>}<DialogFooter><Button variant="outline" disabled={working} onClick={() => setConfirmation(null)}>Cancel</Button><Button disabled={working} onClick={start}>{working && <LoaderCircle className="size-4 animate-spin" />}Confirm & spend Jev tokens</Button></DialogFooter></DialogContent></Dialog>
  </div>
}

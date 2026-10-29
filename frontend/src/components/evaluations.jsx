import { useEffect, useRef, useState } from "react"
import { Play, Square, RefreshCw, Download, FlaskConical, FolderOpen, Check, X, LoaderCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { CopyButton } from "@/components/message"
import { api, shortDate } from "@/lib/api"

const isRunning = status => ["running", "stopping"].includes(status)
const statusLabel = status => status?.replaceAll("_", " ") || "Unknown"
const seconds = milliseconds => milliseconds == null ? "In progress" : `${(milliseconds / 1000).toFixed(1)}s`

export function EvaluationResult({ run }) {
  if (!run) return <div className="rounded-2xl border border-dashed border-border px-6 py-12 text-center"><FlaskConical className="mx-auto mb-4 size-7 text-muted-foreground" /><h2 className="font-medium">Run a suite to see its results</h2><p className="mt-2 text-sm text-muted-foreground">Progress, individual checks, and logs will appear here.</p></div>
  const summary = run.summary
  const failed = summary ? (summary.failures || 0) + (summary.errors || 0) + (summary.unexpected_successes || 0) : null
  function download() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(run, null, 2)], { type: "application/json" }))
    const link = document.createElement("a")
    link.href = url; link.download = `evaluation-${run.id}.json`; link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return <section className="space-y-5" aria-label="Test run results">
    <div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-3"><h2 className="font-medium">{run.name}</h2><Badge variant="secondary" className="gap-1.5 font-normal capitalize">{isRunning(run.status) ? <LoaderCircle className="size-3 animate-spin" /> : run.status === "passed" ? <Check className="size-3" /> : ["failed", "error"].includes(run.status) ? <X className="size-3" /> : null}{statusLabel(run.status)}</Badge></div><Button variant="ghost" size="sm" disabled={isRunning(run.status)} onClick={download}><Download className="size-4" />Export report</Button></div>
    <p className="text-xs text-muted-foreground">{shortDate(run.started_at)} · {seconds(run.elapsed_ms)} · No model request</p>
    {run.error && <p role="alert" className="rounded-xl border border-destructive/30 p-4 text-sm text-destructive">{run.error}</p>}
    {run.status === "no_tests" && <p role="status" className="text-sm text-muted-foreground">No unittest tests were found. Check the folder and use filenames beginning with test. This run is not a pass.</p>}
    {run.source_changed && <p role="status" className="text-sm text-muted-foreground">Source files changed during this run. Review the changes before comparing this result with another run.</p>}
    <div className="grid grid-cols-2 gap-6 border-y border-border py-6 sm:grid-cols-4">{[
      [summary?.checks_run !== undefined ? "Checks run" : "Tests run", summary?.tests_run ?? summary?.checks_run],
      ["Passed", summary?.passed], ["Failures / errors", failed], ["Skipped", summary?.skipped],
    ].map(([label, value]) => <div key={label}><p className="text-xs text-muted-foreground">{label}</p><p className="mt-2 text-2xl font-medium tabular-nums">{value ?? "—"}</p></div>)}</div>
    {!!run.cases?.length && <div className="max-h-[440px] overflow-auto rounded-xl border border-border"><Table><TableHeader><TableRow><TableHead>Check</TableHead><TableHead className="w-28">Result</TableHead></TableRow></TableHeader><TableBody>{run.cases.map((item, i) => <TableRow key={`${item.id}-${i}`}><TableCell className="max-w-[36rem] whitespace-normal break-words text-xs leading-5">{item.detail ? <details><summary className="cursor-pointer font-mono">{item.id}</summary><pre className="mt-3 max-h-60 overflow-auto whitespace-pre-wrap rounded-lg bg-secondary p-3 text-xs leading-6">{item.detail}</pre></details> : <span className="font-mono">{item.id}</span>}</TableCell><TableCell className="align-top text-xs capitalize">{statusLabel(item.status)}</TableCell></TableRow>)}</TableBody></Table></div>}
    {run.cases_truncated && <p className="text-xs text-muted-foreground">Showing the first 1,000 check results.</p>}
    <details open={isRunning(run.status) || ["failed", "error", "timed_out"].includes(run.status)} className="rounded-xl border border-border">
      <summary className="cursor-pointer px-4 py-3 text-sm">Run output</summary><div className="border-t border-border"><div className="flex justify-end px-2 py-1"><CopyButton text={run.output || ""} label="Copy output" /></div><pre className="max-h-80 overflow-auto whitespace-pre-wrap break-words px-4 pb-4 font-mono text-xs leading-6">{run.output || "Waiting for the test runner…"}</pre></div>
    </details>
    {run.output_truncated && <p className="text-xs text-muted-foreground">The output preview retains its most recent 160,000 characters.</p>}
    <details className="text-xs text-muted-foreground"><summary className="cursor-pointer">Run details</summary><div className="mt-3 space-y-2 break-all leading-6"><p>Workspace: {run.workspace}</p><p>Test folder: {run.test_directory}</p><p>Python: {run.python_version}</p><p>Source fingerprint: {run.source_before?.sha256}</p><p>Saved record: {run.record_path}</p><p>These are local {run.scope === "workspace_checks" ? "workspace tests" : "software checks"}, not SWE-bench results.</p></div></details>
  </section>
}

export function Evaluations({ workspace, chat, codingBusy }) {
  const [data, setData] = useState(null)
  const [kind, setKind] = useState("project")
  const [directory, setDirectory] = useState(".")
  const [selected, setSelected] = useState(null)
  const [run, setRun] = useState(null)
  const [refresh, setRefresh] = useState(0)
  const [error, setError] = useState("")
  const [starting, setStarting] = useState(false)
  const pendingRef = useRef(null)
  const sendingRef = useRef(false)

  useEffect(() => {
    let disposed = false, timer
    async function poll() {
      try {
        const next = await api("/evaluations")
        if (disposed) return
        setData(next)
        const id = selected || next.active_id || next.runs[0]?.id
        if (id) {
          const detail = await api(`/evaluations/${id}`)
          if (disposed) return
          setRun(detail)
          if (!selected) setSelected(id)
        }
        if (next.active_id && !disposed) timer = setTimeout(poll, 800)
      } catch (e) { if (!disposed) { setError(e.message); timer = setTimeout(poll, 2000) } }
    }
    poll()
    return () => { disposed = true; clearTimeout(timer) }
  }, [selected, refresh])
  const suite = data?.suites.find(item => item.id === kind)
  const busy = !!data?.active_id
  const selectedWorkspace = chat?.workspace || workspace

  async function start() {
    if (sendingRef.current || busy || codingBusy || !suite?.available) return
    sendingRef.current = true; setStarting(true); setError("")
    const request = { kind, workspace: selectedWorkspace, directory, chat_id: chat?.id || null }
    const signature = JSON.stringify(request)
    if (pendingRef.current?.signature !== signature) pendingRef.current = { signature, id: crypto.randomUUID() }
    try {
      const result = await api("/evaluations", { ...request, request_id: pendingRef.current.id })
      pendingRef.current = null
      setSelected(result.id); setRun(result); setRefresh(v => v + 1)
    } catch (e) { setError(e.message) }
    finally { sendingRef.current = false; setStarting(false) }
  }
  async function stop() {
    try { await api(`/evaluations/${data.active_id}/stop`, {}); setRefresh(v => v + 1) }
    catch (e) { setError(e.message) }
  }

  return <div className="mx-auto w-full max-w-5xl space-y-8 px-5 py-8 md:px-10 md:py-12">
    <div className="flex items-start justify-between gap-4"><div><h1 className="text-2xl font-semibold tracking-tight">Tests & analysis</h1><p className="mt-2 text-sm leading-6 text-muted-foreground">Run checks, inspect failures, and keep a record of each result.</p></div><Button variant="ghost" size="icon" aria-label="Refresh test results" onClick={() => setRefresh(v => v + 1)}><RefreshCw className="size-4" /></Button></div>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <div className="space-y-4 rounded-2xl border border-border p-5">
      <div className="flex flex-wrap items-end gap-3"><div className="min-w-52 flex-1 space-y-2"><label htmlFor="test-suite" className="text-sm font-medium">Test suite</label><Select value={kind} onValueChange={setKind}><SelectTrigger id="test-suite" className="w-full"><SelectValue placeholder="Choose a suite" /></SelectTrigger><SelectContent>{data?.suites.map(item => <SelectItem key={item.id} value={item.id}>{item.name}</SelectItem>)}</SelectContent></Select></div>
        {busy ? <Button variant="outline" onClick={stop}><Square className="size-3.5" />Stop tests</Button> : <Button onClick={start} disabled={starting || codingBusy || !suite?.available}>{starting ? <LoaderCircle className="size-4 animate-spin" /> : <Play className="size-4" />}Run tests</Button>}
      </div>
      <p className="text-sm text-muted-foreground">{suite?.description || "Loading available suites…"}</p>
      {suite && !suite.available && <p className="text-sm text-muted-foreground">This checkout is missing the local test files or required tooling. Tests are kept out of Git at your request.</p>}
      {kind === "workspace" && <div className="space-y-3 border-t border-border pt-4"><p className="flex items-start gap-2 text-xs text-muted-foreground"><FolderOpen className="size-4 shrink-0" /><span className="break-all">{selectedWorkspace}</span></p><label htmlFor="test-directory" className="block text-sm">Test folder, relative to this workspace</label><Input id="test-directory" value={directory} onChange={e => setDirectory(e.target.value)} placeholder=". or tests" /><p className="text-xs leading-5 text-muted-foreground">Runs test*.py with Python unittest. Use local code you trust; network and child commands are disabled in this runner. An isolated runner will handle SWE-bench repositories.</p></div>}
      <p className="text-xs text-muted-foreground">These checks do not call Jev or a coding model. {codingBusy ? "Finish the coding response before starting tests." : "The API budget is unchanged."}</p>
    </div>
    <EvaluationResult run={run} />
    {!!data?.runs.length && <section><h2 className="mb-3 text-sm font-medium">Run history</h2><div className="divide-y divide-border">{data.runs.map(item => <Button key={item.id} variant="ghost" className={`h-auto w-full justify-between gap-3 rounded-none px-3 py-3 text-left font-normal ${selected === item.id ? "bg-secondary/70" : ""}`} onClick={() => setSelected(item.id)}><span><span className="block text-sm">{item.name}</span><span className="mt-1 block text-xs text-muted-foreground">{shortDate(item.started_at)} · {seconds(item.elapsed_ms)}</span></span><span className="text-xs capitalize text-muted-foreground">{statusLabel(item.status)}</span></Button>)}</div></section>}
    <div className="border-t border-border pt-6 text-sm leading-6 text-muted-foreground"><h2 className="mb-1 font-medium text-foreground">Next: SWE-bench evaluation</h2><p>This area will also show task outcomes and strategy comparisons from the isolated benchmark runner. Local test results and token-price estimates remain separate from measured benchmark performance.</p></div>
  </div>
}

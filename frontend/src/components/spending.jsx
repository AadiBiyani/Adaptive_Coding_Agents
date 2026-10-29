import { useEffect, useState } from "react"
import { Calculator, RefreshCw, CircleHelp, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { api, modelName, money, shortDate } from "@/lib/api"

export function Spending({ configurations, budget, onBudget }) {
  const [baseline, setBaseline] = useState("sol-high")
  const [cache, setCache] = useState("30m")
  const [data, setData] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [refresh, setRefresh] = useState(0)
  useEffect(() => {
    let disposed = false
    setLoading(true)
    api(`/spending?baseline=${baseline}&cache=${cache}`).then(result => {
      if (disposed) return
      setData(result)
      setSelectedId(current => result.runs.some(r => r.id === current) ? current : result.runs[0]?.id)
      onBudget(result.budget)
      setError("")
    }).catch(e => { if (!disposed) setError(e.message) }).finally(() => { if (!disposed) setLoading(false) })
    return () => { disposed = true }
  }, [baseline, cache, refresh, onBudget])
  const run = data?.runs.find(r => r.id === selectedId)
  const c = run?.comparison
  const difference = c?.difference_usd === null || c?.difference_usd === undefined ? null : Number(c.difference_usd)
  const maximum = Math.max(Number(c?.routed_total_usd || 0), Number(c?.fixed_coding.amount_usd || 0), .000001)
  const bars = c?.available ? [
    { name: "Routed + Jev", value: c.routed_total_usd, detail: `${modelName(c.selected.model)} / ${c.selected.effort}`, tone: "bg-foreground" },
    { name: "Fixed configuration", value: c.fixed_coding.amount_usd, detail: `${modelName(c.baseline.model)} / ${c.baseline.effort}`, tone: "bg-muted-foreground/35" },
  ] : []

  return <div className="mx-auto w-full max-w-4xl space-y-8 px-5 py-8 md:px-10 md:py-12">
    <div className="flex items-start justify-between gap-4">
      <div><h1 className="text-2xl font-semibold tracking-tight">Spending</h1><p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Compare the observed tokens at another configuration’s prices. The comparison never sends a second prompt.</p></div>
      <Button variant="ghost" size="icon" aria-label="Refresh spending" disabled={loading} onClick={() => setRefresh(v => v + 1)}><RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} /></Button>
    </div>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <div className="grid gap-5 sm:grid-cols-2">
      <div className="space-y-2"><label className="text-sm font-medium" htmlFor="baseline">Compare with</label>
        <Select value={baseline} onValueChange={setBaseline}><SelectTrigger id="baseline" className="w-full"><SelectValue /></SelectTrigger><SelectContent>{configurations.map(config => <SelectItem key={config.id} value={config.id}>{modelName(config.model)} / {config.effort} effort</SelectItem>)}</SelectContent></Select>
      </div>
      <div className="space-y-2"><label className="text-sm font-medium" htmlFor="cache-lifetime">Assumed cache-write lifetime</label>
        <Select value={cache} onValueChange={setCache}><SelectTrigger id="cache-lifetime" className="w-full"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="30m">30 minutes</SelectItem><SelectItem value="12h">12 hours</SelectItem></SelectContent></Select>
      </div>
    </div>
    {!run && !loading && <div className="rounded-2xl border border-dashed border-border px-6 py-12 text-center"><Calculator className="mx-auto mb-4 size-7 text-muted-foreground" /><h2 className="font-medium">Your first comparison starts with a conversation</h2><p className="mt-2 text-sm text-muted-foreground">Send a coding prompt in Chat. Its recorded usage will appear here.</p></div>}
    {run && <>
      <div className="flex flex-wrap items-center justify-between gap-3 text-sm"><span>{shortDate(run.started_at)}</span><Badge variant="secondary" className="font-normal">Fixed-token estimate</Badge></div>
      <div className="grid gap-6 border-y border-border py-6 sm:grid-cols-3">
        <div><p className="text-sm text-muted-foreground">Routed, including Jev</p><p className="mt-2 text-2xl font-medium tracking-tight tabular-nums">{money(c.routed_total_usd)}</p></div>
        <div><p className="text-sm text-muted-foreground">Fixed configuration</p><p className="mt-2 text-2xl font-medium tracking-tight tabular-nums">{money(c.available ? c.fixed_coding.amount_usd : null)}</p></div>
        <div><p className="text-sm text-muted-foreground">Estimated price difference</p><p className="mt-2 text-2xl font-medium tracking-tight tabular-nums">{difference === null ? "Unavailable" : money(Math.abs(difference))}</p>{difference !== null && <p className="mt-1 text-xs text-muted-foreground">{difference >= 0 ? "Lower with the routed configuration" : "Higher with the routed configuration"}</p>}</div>
      </div>
      {!c.available && <p role="status" className="text-sm text-muted-foreground">{c.unavailable_reason}</p>}
      {bars.length > 0 && <div className="space-y-5" aria-label="Estimated cost comparison in US dollars">{bars.map(bar => <div key={bar.name}>
        <div className="mb-2 flex justify-between gap-4 text-sm"><span>{bar.name} <span className="ml-1 text-xs text-muted-foreground">{bar.detail}</span></span><span className="tabular-nums">{money(bar.value)}</span></div>
        <div className="h-2.5 overflow-hidden rounded-full bg-secondary"><div className={`h-full rounded-full ${bar.tone}`} style={{ width: `${Math.max(1, Number(bar.value) / maximum * 100)}%` }} /></div>
      </div>)}</div>}
      <div className="flex gap-3 rounded-xl bg-secondary/65 p-4 text-sm leading-6 text-muted-foreground"><CircleHelp className="mt-1 size-4 shrink-0" /><div><p className="font-medium text-foreground">{c.scope_label}</p><p className="mt-1">This is a pricing scenario, not a verified bill or measured savings. Different models and effort levels may use different token counts. Reasoning is already included in output tokens.</p>{c.scope !== "turn" && <p className="mt-1">This resumed run may include earlier turns. Its snapshot is not added to a total.</p>}</div></div>
      <details className="text-sm"><summary className="cursor-pointer text-muted-foreground">Token breakdown and pricing assumptions</summary><div className="mt-4 space-y-4">
        {c.routed_coding.counts && <Table><TableHeader><TableRow><TableHead>Token category</TableHead><TableHead className="text-right">Observed count</TableHead><TableHead className="text-right">Routed price / 1M</TableHead><TableHead className="text-right">Baseline price / 1M</TableHead></TableRow></TableHeader><TableBody>{Object.entries(c.routed_coding.counts).map(([key, count]) => <TableRow key={key}><TableCell>{{ input: "Uncached input", cached: "Cached input", write: "Cache writes", output: "Output (includes reasoning)" }[key]}</TableCell><TableCell className="text-right tabular-nums">{count.toLocaleString()}</TableCell><TableCell className="text-right">{money(c.routed_coding.rates_per_million[key])}</TableCell><TableCell className="text-right">{money(c.fixed_coding.rates_per_million[key])}</TableCell></TableRow>)}</TableBody></Table>}
        <p>Jev estimate: {money(c.classifier_estimate_usd)}. The fixed configuration has no classifier charge.</p>
        <ul className="list-disc space-y-1 pl-5 text-muted-foreground">{c.assumptions.map(a => <li key={a}>{a}</li>)}</ul>
        <p className="text-xs text-muted-foreground">Rates checked {c.pricing_date}. <a href={c.pricing_sources[0]} target="_blank" rel="noreferrer" className="underline">Luna pricing</a>, <a href={c.pricing_sources[1]} target="_blank" rel="noreferrer" className="underline">Sol pricing</a>, <a href={c.pricing_sources[2]} target="_blank" rel="noreferrer" className="underline">cache pricing</a>.</p>
      </div></details>
    </>}
    {data?.runs.length > 0 && <div><h2 className="mb-3 text-sm font-medium">Recorded runs</h2><div className="divide-y divide-border">{data.runs.map(item => <Button key={item.id} variant="ghost" className={`h-auto w-full justify-between gap-3 rounded-none px-2 py-3 text-left font-normal ${selectedId === item.id ? "bg-secondary/70" : ""}`} onClick={() => setSelectedId(item.id)}><span><span className="block text-sm">{modelName(item.route.configuration.model)} / {item.route.configuration.effort}</span><span className="mt-1 block text-xs text-muted-foreground">{shortDate(item.started_at)} · {item.comparison.scope === "turn" ? "Turn tokens" : "Thread snapshot"}</span></span><span className="flex items-center gap-2 text-xs text-muted-foreground">{item.status}<ChevronRight className="size-4" /></span></Button>)}</div></div>}
    <Separator />
    <div><h2 className="font-medium">Spending limits</h2><p className="mt-1 text-sm text-muted-foreground">The shared budget uses conservative admission estimates, which can differ from the pricing scenario above.</p>
      {budget?.available ? <div className="mt-5 grid gap-5 sm:grid-cols-2">{["openai", "jev"].map(provider => <div key={provider}><div className="flex justify-between text-sm"><span>{provider === "openai" ? "OpenAI" : "Jev"}</span><span>{money(budget.remaining_usd[provider])} remaining</span></div><p className="mt-2 text-xs text-muted-foreground">{budget.attempts_used[provider]} of {budget.attempt_limits[provider]} {provider === "openai" ? "coding turns" : "classifications"} used</p></div>)}</div> : <p className="mt-4 text-sm text-muted-foreground">{budget?.error}</p>}
      {budget?.uncertain && <p className="mt-4 text-sm text-destructive">A request is pending or its final spending is uncertain. New calls may be blocked.</p>}
    </div>
  </div>
}

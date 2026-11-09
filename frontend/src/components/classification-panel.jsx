import { Check, CircleHelp, GitBranch, LoaderCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { modelName } from "@/lib/api"

const fields = { task_type: "Task type", cause_evidence: "Cause evidence", change_scope: "Change scope" }
const label = value => value?.replaceAll("_", " ") || "Unavailable"
const validProbability = value => typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1
const percent = value => validProbability(value) ? `${(100 * value).toFixed(1)}%` : "Unavailable"
const configurationName = config => config ? `${modelName(config.model)} · ${config.effort} effort` : "Unavailable"

export function ClassificationPanel({ turn }) {
  const result = turn.classification
  const route = turn.route
  const waiting = !result && !route && ["running", "stopping"].includes(turn.status)
  const failed = result && result.status !== "ok"
  return <section className="mb-5 overflow-hidden rounded-2xl border border-border" aria-label="Jev classification and routing">
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-secondary/40 px-4 py-3">
      <h3 className="flex items-center gap-2 text-sm font-medium">{waiting ? <LoaderCircle className="size-4 animate-spin" /> : <GitBranch className="size-4" />}Jev classification</h3>
      <span className="text-xs text-muted-foreground">{result?.returned_model || result?.requested_model || "Prompt only"}{result?.elapsed_ms != null ? ` · ${result.elapsed_ms} ms` : ""}</span>
    </div>
    <div className="space-y-4 p-4">
      {waiting ? <p role="status" className="text-sm text-muted-foreground">Waiting for Jev’s categories and probabilities…</p> : failed ? <p className="text-sm text-destructive">{result.error?.message || "Jev did not return a usable classification. No category probabilities are available."}</p> : <>
        <div className="grid gap-4 sm:grid-cols-3">{Object.entries(fields).map(([name, title]) => {
          const answer = result?.answers?.[name]
          const selected = answer?.choice || result?.labels?.[name] || route?.labels?.[name]
          const probabilities = answer?.probabilities && typeof answer.probabilities === "object" ? Object.entries(answer.probabilities) : []
          return <div key={name} className="min-w-0 space-y-3">
            <div><h4 className="text-xs text-muted-foreground">{title}</h4><p className="mt-1 text-sm font-medium">{label(selected)}</p></div>
            {probabilities.length ? <ul className="space-y-2.5" aria-label={`${title} probabilities`}>{probabilities.map(([option, probability]) => <li key={option}>
              <div className={`mb-1 flex items-start justify-between gap-2 text-[11px] leading-4 ${option === selected ? "font-medium" : "text-muted-foreground"}`}><span className="flex items-start gap-1">{option === selected && <Check className="mt-0.5 size-3 shrink-0" aria-label="Selected category" />}{label(option)}</span><span className="shrink-0 tabular-nums">{percent(probability)}</span></div>
              {validProbability(probability) && <div role="meter" aria-label={`${title}: ${label(option)}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={probability * 100} aria-valuetext={percent(probability)} className="h-1.5 overflow-hidden rounded-full bg-secondary"><div className={`h-full rounded-full ${option === selected ? "bg-foreground/80" : "bg-muted-foreground/35"}`} style={{ width: `${probability * 100}%` }} /></div>}
            </li>)}</ul> : <p className="text-xs leading-5 text-muted-foreground">Probabilities were not recorded for this turn.</p>}
          </div>
        })}</div>
        <p className="flex gap-2 text-[11px] leading-5 text-muted-foreground"><CircleHelp className="mt-1 size-3 shrink-0" />These are Jev’s category probabilities, not the chance that a coding model will solve the task. The current policy uses the selected labels.</p>
      </>}
      {route ? <div className="space-y-2 border-t border-border pt-4">
        <div className="flex flex-wrap items-center justify-between gap-2"><h4 className="text-xs font-medium">Why this model & effort</h4>{route.fallback && <Badge variant="outline" className="text-[10px] font-normal">Fallback</Badge>}</div>
        <p className="text-sm font-medium">{configurationName(route.configuration)}</p>
        <p className="text-sm leading-6 text-muted-foreground">{route.reason}</p>
        {turn.configuration_changed && turn.previous_configuration && <p className="text-xs text-muted-foreground">Changed from {configurationName(turn.previous_configuration)} for this user prompt.</p>}
        <p className="text-[11px] leading-5 text-muted-foreground">The routing policy maps Jev’s labels to this configuration. This mapping is provisional; it has not been validated against coding outcomes.</p>
        {turn.accepted && <p className="text-[11px] text-muted-foreground">Codex accepted: {configurationName(turn.accepted)}</p>}
      </div> : result?.status === "ok" && <p className="text-xs text-muted-foreground">{["running", "stopping"].includes(turn.status) ? "The routing policy is selecting an eligible configuration." : "No coding configuration was selected for this turn."}</p>}
      {result && <details className="text-[11px] leading-5 text-muted-foreground"><summary className="w-fit cursor-pointer">Classification details</summary><div className="mt-2 space-y-1"><p>Taxonomy: {result.taxonomy_version || "Unavailable"} · Policy: {route?.policy_version || "Not selected"}</p><p>Requested classifier: {result.requested_model || "Unavailable"} · Returned: {result.returned_model || "Unavailable"}</p>{Object.entries(fields).map(([name, title]) => <p key={name}>{title} — provider confidence: {percent(result.answers?.[name]?.confidence)}</p>)}<p>Provider confidence is reported separately from the option probabilities above. Neither supplies a probability for model selection.</p></div></details>}
    </div>
  </section>
}

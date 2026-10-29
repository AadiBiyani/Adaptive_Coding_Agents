import { useState } from "react"
import { ShieldCheck } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function Approval({ request, onAnswer }) {
  const [answers, setAnswers] = useState({})
  const [waiting, setWaiting] = useState(false)
  const [error, setError] = useState("")
  const questions = request.params.questions || []
  const isQuestion = request.method.endsWith("requestUserInput")
  const allow = !request.params.availableDecisions || request.params.availableDecisions.includes("accept")
  async function respond(decision) {
    setWaiting(true)
    try { await onAnswer({ request_id: request.id, decision, answers: decision === "accept" ? answers : {} }) }
    catch (e) { setError(e.message); setWaiting(false) }
  }
  return <Alert className="mb-6 rounded-2xl"><ShieldCheck className="size-4" /><AlertTitle>{isQuestion ? "The agent has a question" : "Your approval is needed"}</AlertTitle><AlertDescription className="mt-3 block w-full text-foreground">
    {isQuestion ? <div className="space-y-4">{questions.map(q => <div key={q.id} className="space-y-2"><label className="text-sm" htmlFor={`answer-${q.id}`}>{q.question}</label>{q.options?.length > 0 && <p className="text-xs text-muted-foreground">Suggested: {q.options.map(o => o.label).join(" / ")}</p>}<Input id={`answer-${q.id}`} value={answers[q.id] || ""} onChange={e => setAnswers(v => ({ ...v, [q.id]: e.target.value }))} /></div>)}</div> : <>
      {request.params.reason && <p className="mb-3 text-sm">{request.params.reason}</p>}
      <pre className="max-h-60 overflow-auto whitespace-pre-wrap break-all rounded-lg bg-secondary p-3 font-mono text-xs leading-6">{request.params.command || JSON.stringify(request.params.permissions || request.params, null, 2)}</pre>
    </>}
    {error && <p role="alert" className="mt-3 text-sm text-destructive">{error}</p>}
    <div className="mt-4 flex gap-2"><Button size="sm" disabled={waiting || (!isQuestion && !allow)} onClick={() => respond("accept")}>{isQuestion ? "Send answer" : "Allow once"}</Button><Button size="sm" variant="outline" disabled={waiting} onClick={() => respond("decline")}>{isQuestion ? "Skip" : "Decline"}</Button></div>
  </AlertDescription></Alert>
}

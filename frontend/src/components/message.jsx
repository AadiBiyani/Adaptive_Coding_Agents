import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { Check, Copy, FileCode2, ChevronDown, Terminal, CornerDownRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { modelName } from "@/lib/api"

export function CopyButton({ text, label = "Copy", className = "" }) {
  const [copied, setCopied] = useState(false)
  const [failed, setFailed] = useState(false)
  async function copy() {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setFailed(false)
      setTimeout(() => setCopied(false), 1800)
    } catch { setFailed(true) }
  }
  return <Button variant="ghost" size="sm" className={`gap-1.5 text-xs text-muted-foreground ${className}`} onClick={copy} aria-label={copied ? "Copied" : label}>
    {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
    {failed ? "Select and copy" : copied ? "Copied" : label}
  </Button>
}

function CodeBlock({ children }) {
  const child = Array.isArray(children) ? children[0] : children
  const text = String(child?.props?.children || "").replace(/\n$/, "")
  const language = child?.props?.className?.replace("language-", "") || "code"
  return <div className="my-4 overflow-hidden rounded-xl border border-border bg-secondary/60">
    <div className="flex items-center justify-between border-b border-border px-4 py-1.5 text-xs text-muted-foreground">
      <span>{language}</span><CopyButton text={text} label="Copy code" />
    </div>
    <pre className="p-4"><code>{text}</code></pre>
  </div>
}

export function Markdown({ text }) {
  return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml components={{
    pre: CodeBlock,
    a: ({ href, children }) => /^https?:\/\//.test(href || "")
      ? <a href={href} target="_blank" rel="noreferrer noopener">{children}</a>
      : <span className="font-medium">{children}</span>,
  }}>{text}</ReactMarkdown></div>
}

export function Turn({ turn, onFiles }) {
  const config = turn.route?.configuration
  const running = ["running", "stopping"].includes(turn.status)
  const response = turn.messages.map(m => m.text).join("\n\n")
  return <article className="space-y-7 pb-9" aria-label="Conversation turn">
    <div className="flex justify-end"><div className="max-w-[90%] whitespace-pre-wrap break-words rounded-3xl bg-secondary px-5 py-3 text-[15px] leading-7">{turn.prompt}</div></div>
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span className="font-medium text-foreground">Adaptive</span>
        {config && <><span aria-hidden="true">/</span><span>{modelName(config.model)}</span><Badge variant="secondary" className="font-normal capitalize">{config.effort} effort</Badge></>}
        {turn.route?.fallback && <Badge variant="outline" className="font-normal">Fallback</Badge>}
      </div>
      {turn.route && <details className="mb-4 text-xs text-muted-foreground">
        <summary className="w-fit cursor-pointer select-none">Why this route</summary>
        <div className="mt-2 space-y-1 border-l-2 border-border pl-3 leading-6">
          <p>{turn.route.reason}</p>
          <p>{Object.entries(turn.route.labels).map(([key, value]) => `${key.replaceAll("_", " ")}: ${value.replaceAll("_", " ")}`).join(" · ")}</p>
          <p>Provisional policy; model quality and savings have not been established.</p>
        </div>
      </details>}
      {turn.messages.map(message => <Markdown key={message.id} text={message.text} />)}
      {running && <p role="status" className="flex items-center gap-2 py-2 text-sm text-muted-foreground"><span className="size-2 rounded-full bg-foreground motion-safe:animate-pulse" />{turn.stage}</p>}
      {turn.error && <div role="alert" className="mt-4 rounded-lg border border-destructive/30 px-4 py-3 text-sm text-destructive">{turn.error}</div>}
      {!!turn.activity.length && <details className="mt-4 rounded-xl border border-border text-sm">
        <summary className="flex cursor-pointer items-center gap-2 px-4 py-3 text-muted-foreground"><Terminal className="size-4" />Activity <span className="ml-auto text-xs">{turn.activity.length} {turn.activity.length === 1 ? "command" : "commands"}</span><ChevronDown className="size-3.5" /></summary>
        <div className="space-y-4 border-t border-border p-4">{turn.activity.map((item, i) => <div key={item.id || i}>
          <p className="flex gap-2 font-mono text-xs"><CornerDownRight className="mt-0.5 size-3.5 shrink-0" /><span className="break-all">{item.command}</span></p>
          {item.output && <pre className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap rounded-lg bg-secondary p-3 font-mono text-xs leading-6">{item.output}</pre>}
          <p className="mt-1 text-xs text-muted-foreground">{item.status}</p>
        </div>)}</div>
      </details>}
      {!!turn.files.length && <Button variant="outline" size="sm" className="mt-4 gap-2 rounded-lg" onClick={onFiles}><FileCode2 className="size-4" />View {turn.files.length} changed {turn.files.length === 1 ? "file" : "files"}</Button>}
      {!running && response && <div className="mt-3"><CopyButton text={response} label="Copy response" /></div>}
    </div>
  </article>
}

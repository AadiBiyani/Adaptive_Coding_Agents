import { useEffect, useState } from "react"
import { FileCode2, FolderOpen, RefreshCw } from "lucide-react"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CopyButton } from "@/components/message"
import { api } from "@/lib/api"

export function FilesPanel({ open, onOpenChange, chat }) {
  const [listing, setListing] = useState(null)
  const [file, setFile] = useState(null)
  const [error, setError] = useState("")
  const [refresh, setRefresh] = useState(0)
  useEffect(() => {
    if (!open || !chat) return
    let disposed = false
    setError("")
    api(`/chats/${chat.id}/files`).then(data => { if (!disposed) setListing(data) }).catch(e => { if (!disposed) setError(e.message) })
    return () => { disposed = true }
  }, [open, chat?.id, refresh])
  useEffect(() => { setFile(null); setListing(null) }, [chat?.id])
  async function select(path) {
    try { setFile(await api(`/chats/${chat.id}/file?path=${encodeURIComponent(path)}`)); setError("") }
    catch (e) { setError(e.message) }
  }
  return <Sheet open={open} onOpenChange={onOpenChange}><SheetContent className="flex w-full flex-col gap-0 p-0 sm:max-w-2xl">
    <SheetHeader className="border-b border-border p-6"><SheetTitle>Workspace files</SheetTitle><SheetDescription>Code written by the agent is saved here on your computer.</SheetDescription>
      <div className="mt-3 flex items-center gap-2 rounded-lg bg-secondary px-3 py-2 text-xs"><FolderOpen className="size-4 shrink-0" /><span className="min-w-0 flex-1 break-all">{chat?.workspace}</span><CopyButton text={chat?.workspace || ""} label="Copy path" /></div>
    </SheetHeader>
    <div className="flex items-center justify-between px-6 py-3 text-sm"><span>{listing?.files.length || 0} files</span><Button variant="ghost" size="icon-sm" aria-label="Refresh files" onClick={() => setRefresh(v => v + 1)}><RefreshCw className="size-4" /></Button></div>
    {error && <p role="alert" className="px-6 pb-3 text-sm text-destructive">{error}</p>}
    {!listing?.files.length && <div className="px-6 py-10 text-center text-sm text-muted-foreground"><FileCode2 className="mx-auto mb-3 size-6" />No files yet. Ask the agent to create a file, or choose an existing project for a new chat.</div>}
    <ScrollArea className="max-h-48 shrink-0 border-b border-border px-3">{listing?.files.map(path => <Button key={path} variant="ghost" className="mb-0.5 h-auto w-full justify-start gap-2 px-3 py-2 text-left text-xs font-normal" onClick={() => select(path)}><FileCode2 className="size-4 shrink-0" /><span className="truncate">{path}</span></Button>)}</ScrollArea>
    {file ? <div className="flex min-h-0 flex-1 flex-col"><div className="flex items-center justify-between gap-2 border-b border-border px-6 py-3 text-xs"><span className="truncate" title={file.path}>{file.path.split("/").pop()}</span><CopyButton text={file.content} label="Copy code" /></div><pre className="min-h-0 flex-1 overflow-auto p-6 font-mono text-xs leading-6"><code>{file.content}</code></pre></div> : <p className="px-6 py-8 text-sm text-muted-foreground">Select a file to see its contents.</p>}
  </SheetContent></Sheet>
}

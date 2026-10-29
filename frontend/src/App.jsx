import { useCallback, useEffect, useRef, useState } from "react"
import { ArrowUp, Square, SquarePen, PanelLeft, Wallet, FlaskConical, FolderOpen, ChevronDown, Code2, Sun, Moon, X, CircleAlert, LoaderCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Turn } from "@/components/message"
import { FilesPanel } from "@/components/files-panel"
import { Approval } from "@/components/approval"
import { Spending } from "@/components/spending"
import { Evaluations } from "@/components/evaluations"
import { api, bootstrap } from "@/lib/api"

function IconButton({ label, children, ...props }) {
  return <Tooltip><TooltipTrigger asChild><Button variant="ghost" size="icon" aria-label={label} {...props}>{children}</Button></TooltipTrigger><TooltipContent>{label}</TooltipContent></Tooltip>
}

export default function App() {
  const [boot, setBoot] = useState(null)
  const [chats, setChats] = useState([])
  const [chat, setChat] = useState(null)
  const [budget, setBudget] = useState(null)
  const [workspace, setWorkspace] = useState("")
  const [workspaceInput, setWorkspaceInput] = useState("")
  const [workspaceOpen, setWorkspaceOpen] = useState(false)
  const [filesOpen, setFilesOpen] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [tab, setTab] = useState("chat")
  const [draft, setDraft] = useState("")
  const [sending, setSending] = useState(false)
  const [error, setError] = useState("")
  const [dark, setDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const sendingRef = useRef(false)
  const pendingRef = useRef(null)
  const textRef = useRef(null)
  const endRef = useRef(null)
  const followRef = useRef(true)
  const selectionRef = useRef(null)
  const running = !!chat?.turns.some(t => ["running", "stopping"].includes(t.status))
  const empty = !chat?.turns.length
  const updateBudget = useCallback(value => setBudget(value), [])

  useEffect(() => { document.documentElement.classList.toggle("dark", dark) }, [dark])
  useEffect(() => {
    let disposed = false
    bootstrap().then(async data => {
      if (disposed) return
      setBoot(data); setChats(data.chats); setBudget(data.budget); setWorkspace(data.workspace)
      if (data.active_chat) {
        const current = await api(`/chats/${data.active_chat}`)
        if (!disposed) { setChat(current); setWorkspace(current.workspace); selectionRef.current = current.id }
      }
    }).catch(e => { if (!disposed) setError(e.message) })
    return () => { disposed = true }
  }, [])
  useEffect(() => {
    if (!chat || !running) return
    let disposed = false
    let timeout
    async function poll() {
      try {
        const current = await api(`/chats/${chat.id}`)
        if (disposed) return
        if (!current.turns.some(t => ["running", "stopping"].includes(t.status))) {
          const fresh = await bootstrap()
          if (!disposed) { setChat(current); setChats(fresh.chats); setBudget(fresh.budget) }
          return
        }
        setChat(current)
      } catch (e) { if (!disposed) setError(e.message) }
      if (!disposed) timeout = setTimeout(poll, 650)
    }
    timeout = setTimeout(poll, 300)
    return () => { disposed = true; clearTimeout(timeout) }
  }, [chat?.id, running])
  useEffect(() => { if (followRef.current && tab === "chat") endRef.current?.scrollIntoView({ block: "end" }) }, [chat?.revision, tab])
  useEffect(() => {
    const input = textRef.current
    if (input) { input.style.height = "auto"; input.style.height = `${Math.min(input.scrollHeight, 200)}px` }
  }, [draft])

  function newChat() {
    if (running || sending) return
    selectionRef.current = null
    pendingRef.current = null
    setChat(null); setDraft(""); setError(""); setTab("chat"); setMobileNav(false)
    followRef.current = true
    requestAnimationFrame(() => textRef.current?.focus())
  }
  async function selectChat(id) {
    if (running && id !== chat?.id) { setError("Finish or stop the current response before switching conversations."); return }
    selectionRef.current = id
    try {
      const current = await api(`/chats/${id}`)
      if (selectionRef.current !== id) return
      setChat(current); setWorkspace(current.workspace); setTab("chat"); setMobileNav(false); setError("")
      pendingRef.current = null
      followRef.current = true
    } catch (e) { setError(e.message) }
  }
  async function send(event) {
    event.preventDefault()
    if (!draft.trim() || running || sendingRef.current || !boot?.credentials_ready) return
    if (new TextEncoder().encode(draft).length > 16384) { setError("This prototype accepts up to 16 KB per prompt. Shorten the message and try again."); return }
    sendingRef.current = true; setSending(true); setError("")
    try {
      const current = chat || await api("/chats", { workspace })
      setChat(current)
      // Reuse an uncertain submission ID if the user retries after a transport error.
      if (pendingRef.current?.chatId !== current.id || pendingRef.current?.prompt !== draft) {
        pendingRef.current = { chatId: current.id, prompt: draft, id: crypto.randomUUID() }
      }
      const updated = await api(`/chats/${current.id}/messages`, { prompt: draft, submission_id: pendingRef.current.id })
      pendingRef.current = null
      selectionRef.current = current.id
      setChat(updated); setDraft(""); followRef.current = true
      setChats((await api("/chats")).chats)
    } catch (e) { setError(e.message) }
    finally { sendingRef.current = false; setSending(false) }
  }
  async function stop() {
    try { await api(`/chats/${chat.id}/stop`, {}); setChat(await api(`/chats/${chat.id}`)) }
    catch (e) { setError(e.message) }
  }
  const remaining = budget?.available ? Math.max(0, budget.attempt_limits.openai - budget.attempts_used.openai) : null
  const workspaceName = workspace.split("/").filter(Boolean).pop() || "Workspace"
  const sidebar = <div className="flex h-full flex-col bg-sidebar px-3 pb-4 pt-3">
    <div className="mb-5 flex items-center justify-between px-1"><Button variant="ghost" className="gap-2.5 px-2 text-base font-semibold tracking-tight" onClick={newChat}><Code2 className="size-5" />Adaptive</Button><IconButton label="Close sidebar" onClick={() => { setSidebarOpen(false); setMobileNav(false) }}><PanelLeft className="size-4.5" /></IconButton></div>
    <Button variant="ghost" className="h-10 justify-start gap-3 rounded-xl font-normal" onClick={newChat} disabled={running || sending}><SquarePen className="size-4.5" />New chat</Button>
    <Button variant="ghost" className={`mt-1 h-10 justify-start gap-3 rounded-xl font-normal ${tab === "spending" ? "bg-accent" : ""}`} onClick={() => { setTab("spending"); setMobileNav(false) }}><Wallet className="size-4.5" />Spending</Button>
    <Button variant="ghost" className={`mt-1 h-10 justify-start gap-3 rounded-xl font-normal ${tab === "tests" ? "bg-accent" : ""}`} onClick={() => { setTab("tests"); setMobileNav(false) }}><FlaskConical className="size-4.5" />Tests & analysis</Button>
    <p className="mb-2 mt-8 px-3 text-xs text-muted-foreground">Conversations</p>
    <ScrollArea className="min-h-0 flex-1"><div className="space-y-1">{chats.map(c => <Button key={c.id} variant="ghost" className={`h-10 w-full justify-start rounded-lg px-3 text-left text-sm font-normal ${chat?.id === c.id && tab === "chat" ? "bg-accent" : ""}`} onClick={() => selectChat(c.id)}><span className="truncate">{c.title}</span></Button>)}</div>{!chats.length && <p className="px-3 py-2 text-xs leading-5 text-muted-foreground">Your conversations will appear here.</p>}</ScrollArea>
    <div className="mt-4 border-t border-border px-3 pt-4"><div className="flex items-center justify-between text-sm"><span>Local workspace</span><span className="size-1.5 rounded-full bg-foreground" /></div><p className="mt-1 text-xs text-muted-foreground">{remaining === null ? "Budget not initialized" : `${remaining} coding ${remaining === 1 ? "turn" : "turns"} remaining`}</p></div>
  </div>

  return <TooltipProvider delayDuration={250}><div className="flex h-dvh overflow-hidden bg-background">
    {sidebarOpen && <aside className="hidden w-[260px] shrink-0 md:block">{sidebar}</aside>}
    <Sheet open={mobileNav} onOpenChange={setMobileNav}><SheetContent side="left" className="w-[280px] gap-0 p-0" showCloseButton={false}><SheetHeader className="sr-only"><SheetTitle>Navigation</SheetTitle><SheetDescription>Conversations and spending</SheetDescription></SheetHeader>{sidebar}</SheetContent></Sheet>
    <main className="flex min-w-0 flex-1 flex-col">
      <header className="flex h-16 shrink-0 items-center justify-between gap-3 px-3 md:px-6">
        <div className="flex min-w-0 items-center gap-1">
          <div className="md:hidden"><IconButton label="Open sidebar" onClick={() => setMobileNav(true)}><PanelLeft className="size-5" /></IconButton></div>
          {!sidebarOpen && <div className="hidden md:block"><IconButton label="Open sidebar" onClick={() => setSidebarOpen(true)}><PanelLeft className="size-5" /></IconButton></div>}
          <Button variant="ghost" className="min-w-0 gap-2 px-2 text-base font-medium" onClick={() => { setWorkspaceInput(workspace); setWorkspaceOpen(true) }}><span className="truncate">Adaptive</span><span className="text-muted-foreground">Auto</span><ChevronDown className="size-4 text-muted-foreground" /></Button>
        </div>
        <Tabs className="hidden lg:block" value={tab} onValueChange={setTab}><TabsList className="h-9 rounded-full bg-secondary/70 p-1"><TabsTrigger value="chat" className="rounded-full px-4 text-xs">Chat</TabsTrigger><TabsTrigger value="tests" className="rounded-full px-4 text-xs">Tests</TabsTrigger><TabsTrigger value="spending" className="rounded-full px-4 text-xs">Spending</TabsTrigger></TabsList></Tabs>
        <div className="flex items-center gap-1"><IconButton label="View workspace files" disabled={!chat} onClick={() => setFilesOpen(true)}><FolderOpen className="size-4.5" /></IconButton><IconButton label={dark ? "Switch to light mode" : "Switch to dark mode"} onClick={() => setDark(v => !v)}>{dark ? <Sun className="size-4.5" /> : <Moon className="size-4.5" />}</IconButton></div>
      </header>
      {!boot && !error && <div className="flex flex-1 items-center justify-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" />Connecting to your workspace</div>}
      {tab === "tests" && boot ? <div className="min-h-0 flex-1 overflow-y-auto"><Evaluations workspace={workspace} chat={chat} codingBusy={running} /></div> : tab === "spending" && boot ? <div className="min-h-0 flex-1 overflow-y-auto"><Spending configurations={boot.configurations} budget={budget} onBudget={updateBudget} /></div> : <div className={`flex min-h-0 flex-1 flex-col ${empty ? "justify-center pb-[12vh]" : ""}`}>
        {empty ? <div className="mx-auto w-full max-w-3xl px-6 pb-8 text-center"><h1 className="text-[28px] font-medium tracking-tight md:text-[32px]">What can I help you code?</h1><p className="mt-3 text-sm text-muted-foreground">Your prompt. The right configuration. One conversation.</p></div> : <div className="chat-scroll min-h-0 flex-1 overflow-y-auto" onScroll={e => { const el = e.currentTarget; followRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120 }}>
          <div className="mx-auto max-w-3xl px-5 pb-4 pt-8 md:px-6">{chat.turns.map(turn => <Turn key={turn.id} turn={turn} onFiles={() => setFilesOpen(true)} />)}
            {chat.approval && <Approval key={chat.approval.id} request={chat.approval} onAnswer={answer => api(`/chats/${chat.id}/approval`, answer)} />}
            <div ref={endRef} />
          </div>
        </div>}
        <div className="mx-auto w-full max-w-3xl shrink-0 px-4 pb-3 md:px-6">
          {error && <div role="alert" className="mb-3 flex items-start gap-2 rounded-xl border border-destructive/25 px-4 py-3 text-sm text-destructive"><CircleAlert className="mt-0.5 size-4 shrink-0" /><span className="min-w-0 flex-1">{error}</span><Button variant="ghost" size="icon-xs" aria-label="Dismiss error" onClick={() => setError("")}><X className="size-3" /></Button></div>}
          {boot && !boot.credentials_ready && <p className="mb-3 text-center text-sm text-muted-foreground">Add both API keys to your local .env file, then restart the server.</p>}
          <form onSubmit={send} className="rounded-[28px] bg-secondary p-3 shadow-[0_2px_8px_0_#00000005] focus-within:ring-1 focus-within:ring-ring/25">
            <Textarea ref={textRef} value={draft} onChange={e => setDraft(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); send(e) } }} placeholder="Ask a coding question or describe a change…" aria-label="Message your coding agent" rows={1} className="max-h-[200px] min-h-12 resize-none border-0 bg-transparent px-3 py-3 text-[15px] leading-6 shadow-none focus-visible:ring-0 dark:bg-transparent" disabled={!boot} />
            <div className="flex items-center justify-between gap-3 pl-1"><Button type="button" variant="ghost" size="sm" className="max-w-[75%] gap-2 rounded-full text-xs font-normal text-muted-foreground" disabled={running} onClick={() => { setWorkspaceInput(workspace); setWorkspaceOpen(true) }}><FolderOpen className="size-3.5" /><span className="truncate">{workspaceName}</span></Button>
              {running ? <Button type="button" size="icon" className="rounded-full" onClick={stop} aria-label="Stop response"><Square className="size-3.5 fill-current" /></Button> : <Button type="submit" size="icon" className="rounded-full" disabled={!draft.trim() || sending || !boot?.credentials_ready} aria-label="Send message">{sending ? <LoaderCircle className="size-4 animate-spin" /> : <ArrowUp className="size-5" />}</Button>}
            </div>
          </form>
          <p className="mt-2.5 text-center text-[11px] leading-5 text-muted-foreground">Sending uses your API credits. Jev sees this prompt; Codex retains the conversation.</p>
        </div>
      </div>}
    </main>
    <Dialog open={workspaceOpen} onOpenChange={setWorkspaceOpen}><DialogContent className="sm:max-w-lg"><DialogHeader><DialogTitle>Code workspace</DialogTitle><DialogDescription>The agent can read and edit files in this folder. Choose an existing project or use the default workspace.</DialogDescription></DialogHeader><div className="space-y-3 py-3"><label htmlFor="workspace-path" className="text-sm font-medium">Folder on your computer</label><Input id="workspace-path" value={workspaceInput} onChange={e => setWorkspaceInput(e.target.value)} placeholder="/absolute/path/to/project" /><p className="text-xs leading-5 text-muted-foreground">Changing the folder starts a new conversation. Answers and code blocks stay in the chat; files are saved directly in this folder.</p></div><DialogFooter><Button variant="outline" onClick={() => setWorkspaceOpen(false)}>Cancel</Button><Button disabled={running || !workspaceInput.trim()} onClick={() => { if (workspaceInput !== workspace) { newChat(); setWorkspace(workspaceInput.trim()) } setWorkspaceOpen(false) }}>Use workspace</Button></DialogFooter></DialogContent></Dialog>
    <FilesPanel open={filesOpen} onOpenChange={setFilesOpen} chat={chat} />
  </div></TooltipProvider>
}

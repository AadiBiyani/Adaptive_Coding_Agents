import { ClassifierPilot } from "@/components/classifier-pilot"

export function Evaluations({ codingBusy, onBudget }) {
  return <div className="mx-auto w-full max-w-5xl space-y-7 px-5 py-8 md:px-10 md:py-12">
    <div><h1 className="text-2xl font-semibold tracking-tight">Evaluation</h1><p className="mt-2 text-sm leading-6 text-muted-foreground">Measure how Jev understands prompts, then evaluate coding outcomes in the benchmark study.</p></div>
    <section className="rounded-2xl bg-secondary/50 p-5" aria-label="How the classifier pilot works">
      <h2 className="text-sm font-medium">What do the 40 prompts test?</h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">They test whether Jev assigns the right categories. They do not ask a coding model to solve 40 problems.</p>
      <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-6">
        <li><strong>You label the prompt.</strong> Choose its task type, evidence, and scope using only the text shown. These are the expected answers.</li>
        <li><strong>Jev classifies it independently.</strong> After you confirm spending, Jev sees that prompt and the fixed category definitions. It does not see your answers or other prompts.</li>
        <li><strong>Compare the labels.</strong> Accuracy shows agreement with your reviewed answers. Inspect disagreements and unknowns instead of treating them as coding failures.</li>
        <li><strong>Keep the two splits separate.</strong> Use 20 development prompts to inspect the setup. Freeze it, then use the 20 held-out prompts for the final check without further tuning.</li>
      </ol>
      <p className="mt-3 text-xs leading-5 text-muted-foreground">This runs hosted Jev only. It does not train or fine-tune a model, call OpenAI, or measure whether the chosen coding model solves a task.</p>
    </section>
    <ClassifierPilot codingBusy={codingBusy} onBudget={onBudget} />
    <div className="border-t border-border pt-6 text-sm leading-6 text-muted-foreground"><h2 className="mb-1 font-medium text-foreground">Coding benchmarks</h2><p>The SWE-bench and controlled multi-turn evaluations will measure executable task success, cost, and routing changes. Each user turn will retain its classification probabilities and routing explanation, using the same records shown in chat.</p></div>
  </div>
}

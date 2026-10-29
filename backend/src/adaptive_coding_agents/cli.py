"""Prompt-only Jev routing with resumable Codex sessions and explicit budgets."""

import argparse
import json
from pathlib import Path
import select
import sys
import time

from .budget import BudgetLedger, DEFAULT_BUDGET_FILE
from .classification import classify_with_budget
from .classifier_evaluation import evaluate_classifier
from .credentials import load_credentials
from .jev import JevError, build_request
from .records import ContractError, Labels, PROMPT_LIMIT_BYTES, PromptRecord
from .routing import CONFIGURATIONS, DEFAULT_FALLBACK, POLICY_EVIDENCE, POLICY_VERSION, registry_preview, select_route
from .run_records import RunRecordError
from .workflow import check_codex, run_prompt
from .workflow_records import WorkflowRecordError


def safe_text(value: str) -> str:
    """Keep source text readable without allowing terminal control sequences."""
    return "".join(c for c in value if c in "\n\t" or (ord(c) >= 32 and not 127 <= ord(c) <= 159))


class Terminal:
    def __init__(self, timeout_seconds: float):
        self.deadline = time.monotonic() + timeout_seconds

    def _answer(self, prompt: str) -> str:
        print(prompt, file=sys.stderr, end="", flush=True)
        if not sys.stdin.isatty():
            print("[no interactive terminal; declined]", file=sys.stderr)
            return ""
        remaining = max(0, self.deadline - time.monotonic())
        ready, _, _ = select.select([sys.stdin], [], [], remaining)
        return sys.stdin.readline().strip() if ready else ""

    def approve(self, method: str, params: dict | None) -> dict:
        params = params or {}
        print(f"\nCodex request: {safe_text(method)}", file=sys.stderr)
        # JSON escaping also prevents terminal controls in tool-supplied fields.
        print(json.dumps(params, indent=2, ensure_ascii=True), file=sys.stderr)
        if method in ("item/commandExecution/requestApproval", "item/fileChange/requestApproval"):
            allowed = params.get("availableDecisions")
            can_accept = allowed is None or "accept" in allowed
            accepted = can_accept and self._answer("Allow this action once? [y/N] ").lower() == "y"
            return {"decision": "accept" if accepted else "decline"}
        if method == "item/permissions/requestApproval":
            accepted = self._answer("Grant these permissions for this turn? [y/N] ").lower() == "y"
            return {"permissions": params.get("permissions", {}) if accepted else {}, "scope": "turn"}
        if method in ("item/tool/requestUserInput", "tool/requestUserInput"):
            answers = {}
            for question in params.get("questions", []):
                answer = self._answer(safe_text(question.get("question", "Answer")) + " ")
                if answer:
                    answers[question["id"]] = {"answers": [answer]}
            return {"answers": answers}
        if method == "mcpServer/elicitation/request":
            return {"action": "decline", "content": None}
        # No unknown callback may inherit the SDK's accept-by-default behavior.
        raise RuntimeError("Unsupported Codex server request; no action approved.")

    def emit(self, method: str, data: dict) -> None:
        if method == "session/opened":
            print(f"Session: {data['session_id']} (resumed: {data['resumed']})", flush=True)
        elif method == "routing/selected":
            config = data["configuration"]
            print(f"Route: {config['model']} / {config['effort']} ({POLICY_EVIDENCE})", flush=True)
            if data.get("fallback"):
                print("Fallback: " + safe_text(data["reason"]), flush=True)
        elif method == "configuration/accepted":
            print(f"Codex accepted: {data['model']} / {data['effort']}", flush=True)
        elif method in ("item/agentMessage/delta", "item/commandExecution/outputDelta", "item/fileChange/outputDelta"):
            print(safe_text(data.get("delta", "")), end="", flush=True)
        elif method == "item/started":
            item = data.get("item", {})
            if item.get("type") == "commandExecution":
                print("\n$ " + safe_text(item.get("command", "")), flush=True)
            elif item.get("type") == "fileChange":
                print("\nFile changes: " + json.dumps(item.get("changes", []), ensure_ascii=True), flush=True)
        elif method == "turn/completed":
            print("\nCodex turn: " + data["turn"]["status"], flush=True)


def read_prompt(args) -> str:
    if args.prompt is not None:
        return args.prompt
    try:
        with args.prompt_file.open("rb") as stream:
            data = stream.read(PROMPT_LIMIT_BYTES + 1)
    except OSError:
        raise ContractError("input_error", "Unable to read the prompt file.") from None
    if len(data) > PROMPT_LIMIT_BYTES:
        raise ContractError("prompt_too_large", f"This command accepts at most {PROMPT_LIMIT_BYTES} UTF-8 bytes, without truncation.")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise ContractError("invalid_utf8", "The prompt file must be UTF-8 text.") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preview = commands.add_parser("preview", help="Show the exact classifier request and configuration pool; no calls or files.")
    route = commands.add_parser("route", help="Inspect the mapping for labels YOU supply; no classifier prediction or calls.")
    run = commands.add_parser("run", help="Submit one prompt on a new/resumed Codex session; requires --live and an initialized budget.")
    classify = commands.add_parser("classify", help="One real Jev classification, without a coding call; requires --live and budget.")
    evaluate = commands.add_parser("evaluate-classifier", help="Evaluate reviewed prompt-only labels; no coding calls.")
    evaluate.add_argument("--dataset", type=Path, required=True)
    evaluate.add_argument("--split", choices=("development", "held_out"), required=True)
    evaluate.add_argument("--freeze-from", type=Path, help="Completed development report; required for held-out evaluation.")
    check = commands.add_parser("check", help="Explicit API authentication/model catalog check; no inference.")
    credentials = commands.add_parser("credentials", help="Show whether local keys are set, never their values; no network.")
    ui = commands.add_parser("ui", help="Start the localhost chat UI; only user-submitted messages invoke providers.")
    ui.add_argument("--port", type=int, default=8765)
    ui.add_argument("--cwd", type=Path, help="Default existing workspace; otherwise creates ignored runs/workspaces/default.")
    ui.add_argument("--run-dir", type=Path, default=Path("runs/coding"))
    ui.add_argument("--chat-dir", type=Path, default=Path("runs/ui/chats"))
    budget = commands.add_parser("budget", help="Initialize or inspect a persistent spending ledger; no network.")
    budget_commands = budget.add_subparsers(dest="budget_command", required=True)
    initialize = budget_commands.add_parser("init")
    status = budget_commands.add_parser("status")
    for sub in (initialize, status, run, classify, evaluate, ui):
        sub.add_argument("--budget-file", type=Path, default=DEFAULT_BUDGET_FILE)
    initialize.add_argument("--jev-usd", required=True)
    initialize.add_argument("--openai-usd", required=True)
    initialize.add_argument("--max-jev-requests", type=int, required=True)
    initialize.add_argument("--max-coding-turns", type=int, required=True)
    for sub in (preview, run, classify):
        source = sub.add_mutually_exclusive_group(required=True)
        source.add_argument("--prompt", help="The complete current user prompt.")
        source.add_argument("--prompt-file", type=Path, help="Read the exact UTF-8 prompt from this file.")
    for sub in (preview, run, check):
        sub.add_argument("--cwd", type=Path, default=Path.cwd(), help="Coding workspace; never sent to Jev.")
    for sub in (run, classify, check, credentials, evaluate, ui):
        env = sub.add_mutually_exclusive_group()
        env.add_argument("--env-file", type=Path, default=Path(".env"), help="Read only this local file; existing environment values take precedence.")
        env.add_argument("--no-env", action="store_true", help="Read credentials only from the inherited environment.")
    for sub, directory in ((run, "coding"), (classify, "jev"), (check, "preflight"), (evaluate, "classifier-evaluation")):
        sub.add_argument("--live", action="store_true", help="Enable the explicitly requested provider operation.")
        sub.add_argument("--run-dir", type=Path, default=Path("runs") / directory)
    for name, values in Labels.OPTIONS.items():
        route.add_argument("--" + name.replace("_", "-"), choices=values, required=True)
    route.add_argument("--fallback", choices=[c.id for c in CONFIGURATIONS], default=DEFAULT_FALLBACK)
    run.add_argument("--fallback", choices=[c.id for c in CONFIGURATIONS], default=DEFAULT_FALLBACK)
    run.add_argument("--session", help="Resume the session_id printed by a previous invocation, using the same workspace and budget.")
    for sub in (run, check, ui):
        sub.add_argument("--timeout-seconds", type=float, default=180, help="Codex process timeout (up to 600s); not an exact billing cap.")
    args = parser.parse_args(argv)
    if args.command in ("run", "classify", "check", "evaluate-classifier") and not args.live:
        parser.error("This command requires --live; use preview for a free local check.")
    try:
        if args.command == "ui":
            from .web_ui import serve
            workspace = args.cwd or Path("runs/workspaces/default")
            if args.cwd is None:
                workspace.mkdir(parents=True, exist_ok=True, mode=0o700)
            serve(port=args.port, workspace=workspace, run_dir=args.run_dir, chat_dir=args.chat_dir,
                  budget_file=args.budget_file, credentials=load_credentials(None if args.no_env else args.env_file),
                  timeout_seconds=args.timeout_seconds)
            return 0
        if args.command == "budget":
            with BudgetLedger(args.budget_file) as ledger:
                details = (ledger.initialize(jev_usd=args.jev_usd, openai_usd=args.openai_usd,
                    max_jev_requests=args.max_jev_requests, max_coding_turns=args.max_coding_turns)
                    if args.budget_command == "init" else ledger.summary())
            result = {"status": "completed", **details}
        elif args.command == "credentials":
            keys = load_credentials(None if args.no_env else args.env_file)
            result = {"status": "preview", "request_attempted": False,
                      "TYPESAFE_API_KEY_set": bool(keys.typesafe), "OPENAI_API_KEY_set": bool(keys.openai)}
        elif args.command == "evaluate-classifier":
            keys = load_credentials(None if args.no_env else args.env_file)
            result = evaluate_classifier(dataset=args.dataset, split=args.split, api_key=keys.typesafe,
                budget_file=args.budget_file, output_root=args.run_dir, freeze_from=args.freeze_from)
        elif args.command == "check":
            keys = load_credentials(None if args.no_env else args.env_file)
            terminal = Terminal(args.timeout_seconds)
            result = check_codex(cwd=args.cwd, openai_api_key=keys.openai, run_dir=args.run_dir,
                timeout_seconds=args.timeout_seconds, approval_handler=terminal.approve, emit=terminal.emit)
        elif args.command == "route":
            labels = Labels(**{name: getattr(args, name) for name in Labels.OPTIONS})
            result = {"status": "preview", "label_source": "user_supplied_for_policy_inspection",
                      "request_attempted": False, "route": select_route(labels, fallback_id=args.fallback).to_dict()}
        else:
            prompt = read_prompt(args)
            PromptRecord.capture(prompt)
            if args.command == "preview":
                result = {"status": "preview", "request_attempted": False,
                          "classifier_request": build_request(prompt), "registry": registry_preview(),
                          "policy_version": POLICY_VERSION, "policy_evidence": POLICY_EVIDENCE,
                          "selected_configuration": None, "coding_workspace": str(args.cwd.resolve())}
            else:
                keys = load_credentials(None if args.no_env else args.env_file)
                if args.command == "classify":
                    with BudgetLedger(args.budget_file) as ledger:
                        result = classify_with_budget(prompt, api_key=keys.typesafe, ledger=ledger, run_dir=args.run_dir)
                        result["budget"] = ledger.summary()
                else:
                    terminal = Terminal(args.timeout_seconds)
                    result = run_prompt(prompt, cwd=args.cwd, api_key=keys.typesafe, openai_api_key=keys.openai,
                        run_dir=args.run_dir, budget_file=args.budget_file, session_id=args.session,
                        fallback_id=args.fallback, timeout_seconds=args.timeout_seconds,
                        approval_handler=terminal.approve, emit=terminal.emit)
        failed = result["status"] not in ("preview", "completed", "ok")
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False), file=sys.stderr if failed else sys.stdout)
        return 130 if result["status"] == "interrupted" else int(failed)
    except WorkflowRecordError as exc:
        print(json.dumps({"status": "error", "record_path": str(exc.path),
                          "error": {"code": "recording_error", "message": str(exc)},
                          "observed_result": exc.observed_result}, indent=2), file=sys.stderr)
        return 1
    except RunRecordError as exc:
        print(json.dumps(exc.to_dict(), indent=2), file=sys.stderr)
        return 1
    except (ContractError, JevError) as exc:
        print(json.dumps({"status": "error", "error": {"code": exc.code, "message": str(exc)}}, indent=2), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"status": "error", "error": {"code": "local_storage_error",
              "message": "A local file operation failed; inspect pending records before retrying."}}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

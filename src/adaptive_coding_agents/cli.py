"""Preview a prompt, inspect a provisional route, or run one coding turn."""

import argparse
import json
import os
from pathlib import Path
import select
import sys
import time

from .jev import build_request
from .records import ContractError, Labels, PROMPT_LIMIT_BYTES, PromptRecord
from .routing import POLICY_EVIDENCE, POLICY_VERSION, registry_preview, select_route
from .workflow import run_prompt
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
        if method == "routing/selected":
            config = data["configuration"]
            print(f"Route: {config['model']} / {config['effort']} ({POLICY_EVIDENCE})", flush=True)
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
        raise ContractError("prompt_too_large", f"This Part 1 command accepts at most {PROMPT_LIMIT_BYTES} UTF-8 bytes, without truncation.")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise ContractError("invalid_utf8", "The prompt file must be UTF-8 text.") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preview = commands.add_parser("preview", help="Show the exact classifier request and configuration pool; no calls or files.")
    route = commands.add_parser("route", help="Inspect the mapping for labels YOU supply; no classifier prediction or calls.")
    run = commands.add_parser("run", help="Execute one prompt through real Jev and Codex; requires --live.")
    for sub in (preview, run):
        source = sub.add_mutually_exclusive_group(required=True)
        source.add_argument("--prompt", help="The complete current user prompt.")
        source.add_argument("--prompt-file", type=Path, help="Read the exact UTF-8 prompt from this file.")
        sub.add_argument("--cwd", type=Path, default=Path.cwd(), help="Coding workspace; never sent to Jev.")
    for name, values in Labels.OPTIONS.items():
        route.add_argument("--" + name.replace("_", "-"), choices=values, required=True)
    run.add_argument("--live", action="store_true", help="Explicitly enable paid-capable Jev and Codex execution after reviewing the run estimate.")
    run.add_argument("--run-dir", type=Path, default=Path("runs/coding"))
    run.add_argument("--timeout-seconds", type=float, default=180, help="Codex process timeout (up to 600 seconds); Jev has a separate socket timeout. Not a dollar cap.")
    args = parser.parse_args(argv)
    if args.command == "run" and not args.live:
        parser.error("run requires --live and can consume credits; use preview for a free local check.")
    try:
        if args.command == "route":
            labels = Labels(**{name: getattr(args, name) for name in Labels.OPTIONS})
            result = {"status": "preview", "label_source": "user_supplied_for_policy_inspection",
                      "request_attempted": False, "route": select_route(labels).to_dict()}
        else:
            prompt = read_prompt(args)
            PromptRecord.capture(prompt)
            if args.command == "preview":
                result = {"status": "preview", "request_attempted": False,
                          "classifier_request": build_request(prompt), "registry": registry_preview(),
                          "policy_version": POLICY_VERSION, "policy_evidence": POLICY_EVIDENCE,
                          "selected_configuration": None, "coding_workspace": str(args.cwd.resolve())}
            else:
                terminal = Terminal(args.timeout_seconds)
                result = run_prompt(prompt, cwd=args.cwd, api_key=os.environ.get("TYPESAFE_API_KEY", ""),
                                    run_dir=args.run_dir, timeout_seconds=args.timeout_seconds,
                                    approval_handler=terminal.approve, emit=terminal.emit)
        failed = result["status"] not in ("preview", "completed")
        print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False), file=sys.stderr if failed else sys.stdout)
        return 130 if result["status"] == "interrupted" else int(failed)
    except WorkflowRecordError as exc:
        print(json.dumps({"status": "error", "record_path": str(exc.path),
                          "error": {"code": "recording_error", "message": str(exc)},
                          "observed_result": exc.observed_result}, indent=2), file=sys.stderr)
        return 1
    except ContractError as exc:
        print(json.dumps({"status": "error", "error": {"code": exc.code, "message": str(exc)}}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

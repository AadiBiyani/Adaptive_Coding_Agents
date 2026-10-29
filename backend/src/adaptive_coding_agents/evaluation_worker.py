"""Structured unittest output for local checks; not a SWE-bench evaluator.

Runs in its own process. Workspace mode disables ordinary Python network and
child-process calls as a spending guard. It is not an untrusted-code sandbox.
"""

import argparse
from pathlib import Path
import sys
import unittest

from .run_records import _write_json


def restrict_workspace_calls(event, args):
    if event in {"socket.connect", "socket.getaddrinfo", "subprocess.Popen", "os.system",
                 "os.posix_spawn", "os.exec", "os.fork", "os.forkpty"}:
        raise PermissionError("Network and child commands are disabled for local workspace checks.")


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, output, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = output
        self.cases = []
        self.passed = 0

    def add_case(self, test, status, detail=None):
        if len(self.cases) < 1000:
            self.cases.append({"id": test.id(), "status": status, "detail": (detail or "")[-8000:]})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed += 1
        self.add_case(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.add_case(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.add_case(test, "error", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.add_case(test, "skipped", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.add_case(test, "expected_failure", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.add_case(test, "unexpected_success")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.add_case(subtest, "failed" if issubclass(err[0], test.failureException) else "error",
                          self._exc_info_to_string(err, subtest))

    def stopTest(self, test):
        super().stopTest(test)
        self.publish("running")

    def publish(self, status):
        _write_json(self.output, {"schema_version": "local-test-result-1", "status": status,
            "summary": {"tests_run": self.testsRun, "passed": self.passed,
                "failures": len(self.failures), "errors": len(self.errors), "skipped": len(self.skipped),
                "expected_failures": len(self.expectedFailures), "unexpected_successes": len(self.unexpectedSuccesses)},
            "cases": self.cases, "cases_truncated": len(self.cases) >= 1000})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", action="store_true")
    args = parser.parse_args(argv)
    directory, output = args.directory.resolve(), args.output.resolve()
    if args.workspace:
        sys.addaudithook(restrict_workspace_calls)
    # -I keeps the launcher isolated; test imports get only the selected folder.
    sys.path.insert(0, str(directory))
    result = None
    def factory(*a, **kw):
        nonlocal result
        result = RecordedResult(*a, output=output, **kw)
        return result
    try:
        suite = unittest.defaultTestLoader.discover(str(directory), pattern="test*.py")
        result = unittest.TextTestRunner(verbosity=2, resultclass=factory).run(suite)
        status = "passed" if result.wasSuccessful() else "failed"
        if result.testsRun == 0:
            status = "no_tests"
        elif len(result.skipped) == result.testsRun:
            status = "skipped"
        result.publish(status)
        return 0 if status == "passed" else 1
    except Exception as exc:
        _write_json(output, {"schema_version": "local-test-result-1", "status": "error",
                            "summary": None, "cases": [], "error": f"Test discovery failed: {type(exc).__name__}: {exc}"})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Write authored review examples, never human labels or experimental results."""

import argparse
import json
import os
from pathlib import Path

from adaptive_coding_agents.taxonomy import TAXONOMY_VERSION

# Each pair is one group. Related prompts stay in the same split. These are
# diagnostic examples authored for the pilot, not a representative SWE-bench set.
GROUPS = [
    ("empty-list", "Fix only last_item: def last_item(xs): return xs[-1]. For [] it raises IndexError; return None instead, while [1, 2] must return 2.",
     "Please try another approach."),
    ("mutable-default", "Diagnose why this Python function keeps old values between calls: def collect(x, bucket=[]): bucket.append(x); return bucket. Explain the cause only; keep the investigation within this function.",
     "Fix only collect's mutable-default bug. collect(1) and then collect(2) should return [1] and [2], respectively."),
    ("parser-cache", "Fix the interaction between parser.py and cache.py: changing the parser's delimiter leaves the cache key unchanged, so parse('a;b', ';') reuses the previous comma-delimited result. Coordinate the parser configuration and cache key.",
     "I suspect a stale cache. Investigate the cause without changing anything."),
    ("division", "Review only mean(values): its new implementation returns sum(values) / len(values). Verify nonempty means and document what currently happens for an empty list; do not repair it.",
     "Check the previous change once more."),
    ("path-prefix", "Fix only is_child(path, root). It uses str(path).startswith(str(root)), accepting /tmp/application under /tmp/app. Require actual path ancestry.",
     "Investigate whether path normalization is causing our failure; I have no reproduction yet."),
    ("timeout", "Diagnose the interaction between client.py retries and worker.py deadlines: three 5-second retries exceed the worker's 10-second timeout. Explain the cause without editing either component.",
     "Run the existing tests and tell me what failed."),
    ("sorting", "Validate only sort_versions. The previous repair should order ['1.9', '1.10'] as ['1.9', '1.10']; add tests without changing the implementation.",
     "Fix only sort_versions; my hypothesis is that it compares strings instead of version tuples."),
    ("mixed", "Build a new React dashboard and separately investigate a Python memory leak. Neither task has priority.",
     "Make it better."),
    ("off-by-one", "Diagnose only inclusive_range: list(range(start, end)) omits end. For start=2, end=4, observed [2,3], expected [2,3,4]. Explain the bug without implementing a fix.",
     "Fix the off-by-one bug in inclusive_range; start=2,end=4 must include 4."),
    ("missing-scope", "Our service returns HTTP 500 whenever a request lacks the optional locale field; it should use 'en'. Please repair this.",
     "Maybe a default argument is wrong. Please fix it."),
    ("dict-delete", "Fix only prune(mapping): deleting keys inside 'for key in mapping' raises RuntimeError: dictionary changed size during iteration. Remove entries whose value is None.",
     "That did not solve it; retry."),
    ("iterator", "Diagnose why this function returns an empty list for generators: def positive(xs): print(list(xs)); return [x for x in xs if x > 0]. Limit the explanation to this function; do not edit.",
     "Validate only positive with a generator yielding -1, 0, 2. Expect [2]; test the existing patch without modifying it."),
    ("timezone", "Repair the interaction between serializer.py and scheduler.py: serializer drops UTC timezone information and scheduler treats the resulting datetime as local time. Preserve the same instant across both components.",
     "I think timezones explain the bug. Diagnose only scheduler.py; I have not collected an error message."),
    ("rounding", "Review only money_total: the implementation uses Decimal constructed from strings. Verify that inputs '0.1' and '0.2' sum exactly to Decimal('0.3'); do not change production code.",
     "Revisit that review, please."),
    ("regex", "Fix only matches_id: re.match(r'[0-9]+', text) accepts '12oops'. The entire string should contain digits, and '' should be rejected.",
     "Could a regular expression be responsible? Investigate the failure without editing files."),
    ("resource", "Diagnose the interaction between loader.py and scanner.py: loader closes a file before returning its iterator; scanner then raises ValueError: I/O operation on closed file. Explain the lifecycle bug without repairing it.",
     "Confirm whether the code is correct now."),
    ("boolean", "Validate only parse_bool: 'false' should return False, 'true' should return True, and other text should raise ValueError. Review the patch and add regression tests without changing the parser.",
     "I suspect parse_bool calls bool() on a string. Repair only that function; I do not have an example yet."),
    ("outside-domain", "Write a marketing page and also explain an unrelated Python exception. Treat both requests as equally important.",
     "Continue."),
    ("slice", "Diagnose only tail(xs, n): it returns xs[-n:], so n=0 returns the entire list. Expected tail([1,2],0) is []. Explain the cause without a repair.",
     "Fix only tail so n=0 gives [], n=1 gives the final item, and positive n larger than the list length gives the full list."),
    ("encoding", "Uploads containing café fail with UnicodeDecodeError; the API should accept UTF-8 text. Fix this failure.",
     "An encoding mismatch might be involved. Please repair it."),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/classifier-pilot.json"))
    args = parser.parse_args()
    examples = []
    for index, (group, first, second) in enumerate(GROUPS):
        for turn, prompt in enumerate((first, second), 1):
            examples.append({"id": f"{group}-{turn}", "group_id": group,
                "split": "development" if index < 10 else "held_out", "prompt": prompt,
                "annotation_input": "current_prompt_only", "labels": None,
                "review": {"status": "pending", "reviewer_id": None, "reviewed_at": None}})
    data = {"schema_version": "classifier-pilot-1", "taxonomy_version": TAXONOMY_VERSION,
        "source": "assistant_authored_diagnostic_prompts; no labels reviewed",
        "examples": examples}
    args.output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
    print(f"Created {args.output}: 20 development + 20 held-out prompts. All labels await human review. No API calls.")


if __name__ == "__main__":
    main()

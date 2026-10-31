import json
import time
from pathlib import Path

from reviewer.core import review_diff

ROOT = Path(__file__).resolve().parent.parent
DIFF_DIR = ROOT / "data" / "sample_diffs"
EXPECTED = json.loads((ROOT / "data" / "expected_issues.json").read_text(encoding="utf-8"))


def issue_text(issue) -> str:
    return f"{issue.title} {issue.explanation} {issue.suggested_fix}".lower()


def is_caught(expected_issue: dict, found_issues):
    for issue in found_issues:
        if issue.category == expected_issue["category"] and any(
            keyword in issue_text(issue) for keyword in expected_issue["keywords"]):
                return True
    return False

def safe_review(diff_text, attempts=4):
    """Call the reviewer, retrying when the model returns broken JSON."""
    for attempt in range(1, attempts + 1):
        try:
            return review_diff(diff_text)
        except Exception as error:
            print(f"   (attempt {attempt} failed: {str(error)[:80]}... retrying)")
            time.sleep(5)
    raise RuntimeError("Reviewer failed after several attempts")


def main():
    total_expected = 0
    total_caught = 0
    false_alarms = 0
    rows = []

    for name, entry in sorted(EXPECTED.items()):
        diff_text = (DIFF_DIR / name).read_text(encoding="utf-8")
        result = safe_review(diff_text)
        expected_issues = entry["expected_issues"]

        caught = sum(is_caught(e, result.issues) for e in expected_issues)
        total_expected += len(expected_issues)
        total_caught += caught

        alarms = 0
        if not expected_issues:
            alarms = sum(1 for i in result.issues if i.severity in ("critical", "major"))
            false_alarms += alarms

        rows.append(
            {
                "diff": name,
                "expected": len(expected_issues),
                "caught": caught,
                "issues_reported": len(result.issues),
                "false_alarms": alarms,
            }
        )
        print(f"{name:28} expected={len(expected_issues)} caught={caught} "
              f"reported={len(result.issues)} false_alarms={alarms}")
        time.sleep(2)

    summary = {
        "total_expected": total_expected,
        "total_caught": total_caught,
        "recall": round(total_caught / total_expected, 2),
        "false_alarms_on_clean_pr": false_alarms,
        "details": rows,
    }
    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "eval_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nCaught {total_caught}/{total_expected} planted issues "
          f"(recall {summary['recall']}), false alarms: {false_alarms}")


if __name__ == "__main__":
    main()
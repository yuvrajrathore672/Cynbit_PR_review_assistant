import sys
from pathlib import Path

from reviewer.core import review_diff

if len(sys.argv) != 2:
    raise SystemExit("Usage: python -m scripts.run_one <path-to-diff>")

diff_text = Path(sys.argv[1]).read_text(encoding="utf-8")
result = review_diff(diff_text)
print(result.model_dump_json(indent=2))
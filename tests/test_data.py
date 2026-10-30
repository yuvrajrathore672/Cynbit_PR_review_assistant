import json
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent/"data"
diff_dir = data_dir/"sample_diffs"

valid_categories = {'security','performance','testing','style','correctness'}

def load_expected():
    with open(data_dir/'expected_issues.json',encoding='utf-8') as f:
        return json.load(f)


def test_every_diff_has_expected_entry():
    expected = load_expected()
    diff_names = {p.name for p in diff_dir.glob("*.diff")}
    assert diff_names == set(expected.keys())

def test_diffs_look_like_git_diffs():
    for path in diff_dir.glob("*.diff"):
        text = path.read_text(encoding="utf-8")
        assert text.startswith('diff --git'), f"{path.name} is not a git diff"
        assert "+++ "in text 

def test_expected_entries_are_well_formed():
    for name,entry in load_expected().items():
        assert "expected_issues" in entry 
        for issue in entry['expected_issues']:
            assert issue['category'] in valid_categories
            assert issue['keywords'], f"{name} has an issue with no keywords"



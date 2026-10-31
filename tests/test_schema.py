import pytest
from pydantic import ValidationError

from reviewer.schemas import ReviewResult

VALID = {
    "summary": "Looks fine",
    "issues": [],
    "scores": {"correctness": 5, "tests": 4, "security": 5, "readability": 5},
    "mentor_comment": "Nice work",
}


def test_valid_review_parses():
    result = ReviewResult.model_validate(VALID)
    assert result.scores.tests == 4
    assert result.issues == []


def test_invalid_severity_is_rejected():
    bad = {
        **VALID,
        "issues": [
            {
                "file": "a.py",
                "severity": "scary", 
                "category": "security",
                "title": "x",
                "explanation": "x",
                "suggested_fix": "x",
            }
        ],
    }
    with pytest.raises(ValidationError):
        ReviewResult.model_validate(bad)
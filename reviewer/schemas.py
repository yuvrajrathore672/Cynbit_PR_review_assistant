from typing import Literal
from pydantic import BaseModel, Field

class Issue(BaseModel):
    file : str
    line : int
    severity : Literal["critical", "major", "minor", "nit"]
    category : Literal["security", "performance", "testing", "correctness", "style"]
    title : str
    explanation : str
    suggested_fix : str


class RubricScores(BaseModel):
    correctness : int= Field(ge=1,le=5)
    tests : int= Field(ge=1,le=5)
    security : int= Field(ge=1,le=5)


class ReviewResult(BaseModel):
    summary: str
    issues : list[Issue]
    scores: RubricScores
    mentor_feedback : str


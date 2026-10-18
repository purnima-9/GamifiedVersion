from pydantic import BaseModel, Field
from typing import Literal


class AnswerOption(BaseModel):
    option_id: str
    label: str
    dimension_values: dict[str, float] = {}


class SurveyQuestion(BaseModel):
    question_id: str
    text: str
    question_type: Literal[
        "single_choice",
        "multiple_choice",
        "likert",
        "price_input",
    ]
    dimension_mappings: dict[str, float] = {}
    options: list[AnswerOption] = []
    required: bool = False
    depends_on: str | None = None
    show_if_option_id: str | None = None
    estimated_seconds: int = Field(default=15, ge=1)


class SurveyBlueprint(BaseModel):
    research_id: int
    title: str
    questions: list[SurveyQuestion]

from pydantic import BaseModel, Field


class AdaptiveNextRequest(BaseModel):
    current_coverage: dict[str, float] = Field(default_factory=dict)
    answered_question_ids: list[str] = Field(default_factory=list)
    response_options: dict[str, str] = Field(default_factory=dict)
    asked_count: int = Field(default=0, ge=0)
    max_questions: int = Field(default=10, ge=1)


class AdaptiveNextResponse(BaseModel):
    status: str
    next_question: dict | None = None
    scores: list[dict] = Field(default_factory=list)
    weighted_coverage: float
    target_attainment: float
    dimension_coverage: dict[str, float]
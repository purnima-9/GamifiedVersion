from pydantic import BaseModel, Field


class CreateAdaptiveSessionRequest(BaseModel):
    research_id: int = Field(gt=0)
    topic: str = Field(min_length=3)
    target_audience: str = "Target respondents"
    geography: str = "Not specified"
    dimensions: list[str] = Field(min_length=1)
    research_plan: dict
    max_questions: int = Field(default=10, ge=1, le=50)
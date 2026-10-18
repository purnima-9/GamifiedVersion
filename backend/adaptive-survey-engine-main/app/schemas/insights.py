from pydantic import BaseModel, Field


class ResearchInsight(BaseModel):
    insight: str
    evidence: str
    caveat: str


class InsightReport(BaseModel):
    session_id: int
    respondent_count: int
    insights: list[ResearchInsight] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
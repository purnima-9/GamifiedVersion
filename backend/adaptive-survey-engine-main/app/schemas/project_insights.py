from pydantic import BaseModel, Field


class ProjectInsight(BaseModel):
    insight: str
    evidence: str
    caveat: str


class ProjectInsightReport(BaseModel):
    research_id: int
    respondent_count: int
    insights: list[ProjectInsight] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
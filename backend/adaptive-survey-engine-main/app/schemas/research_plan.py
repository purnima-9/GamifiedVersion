from pydantic import BaseModel


class ResearchConstruct(BaseModel):
    name: str
    dimension: str
    measurement_method: str


class ResearchHypothesis(BaseModel):
    hypothesis_id: str
    statement: str
    dimension: str


class ResearchPlan(BaseModel):
    research_id: int
    research_objectives: list[str]
    constructs: list[ResearchConstruct]
    hypotheses: list[ResearchHypothesis]

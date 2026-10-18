from pydantic import BaseModel, Field

class ResearchDimensionInput(BaseModel):
    name: str = Field(min_length=1)
    importance: float = Field(ge=1, le=10)
    target_coverage: float = Field(ge=0.0, le=1.0)

class ResearchCreate(BaseModel):
    topic: str = Field(min_length=3)
    target_audience: str
    geography: str
    dimensions: list[ResearchDimensionInput] = Field(min_length=1)

class ResearchResponse(BaseModel):
    id: int
    topic: str
    target_audience: str
    geography: str
    status: str
from app.schemas.research_plan import ResearchPlan
from app.services.gemini_client import generate_structured_output


def generate_research_plan_with_llm(
    research_id: int,
    topic: str,
    target_audience: str,
    geography: str,
    dimensions: list[str],
) -> ResearchPlan:

    prompt = f"""
You are a senior market research strategist.

Create a research plan for the following study.

Topic: {topic}
Target audience: {target_audience}
Geography: {geography}
Research dimensions: {dimensions}

Requirements:
- Create 3 to 5 specific, decision-oriented research objectives.
- Create one measurable construct for each supplied dimension.
- Each construct must have a clear measurement method.
- Create at least one testable hypothesis per dimension.
- Hypotheses must be testable through survey responses.
- Use only the supplied research dimensions.
- Avoid fabricated market statistics or unsupported factual claims.
- Keep the plan practical for a product-launch decision.
"""

    result = generate_structured_output(prompt, ResearchPlan)

    # Keep the research ID supplied by our application.
    result.research_id = research_id

    expected_dimensions = set(dimensions)
    actual_dimensions = {item.dimension for item in result.constructs}

    if not expected_dimensions.issubset(actual_dimensions):
        raise ValueError("Research plan did not cover every supplied dimension.")

    return result
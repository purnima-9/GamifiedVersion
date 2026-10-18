from app.schemas.project_insights import ProjectInsightReport
from app.services.gemini_client import generate_structured_output


def generate_project_insights(report: dict) -> ProjectInsightReport:
    prompt = f"""
You are a market research analyst.

Analyze these aggregated survey results.

Rules:
- Use only the supplied data.
- Never invent percentages, counts, quotations, or trends.
- Every insight must cite specific question results and counts.
- Distinguish observed data from interpretation.
- Mention sample-size, adaptive-question, and sampling limitations.
- Do not claim statistical significance or causation.
- If the data is insufficient, explicitly say so.

Data:
{report}
"""

    result = generate_structured_output(prompt, ProjectInsightReport)

    if result.research_id != report["research_id"]:
        raise ValueError("Incorrect research ID in generated insights.")

    if result.respondent_count != report["eligible_sessions"]:
        raise ValueError("Incorrect respondent count in generated insights.")

    return result
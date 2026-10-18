from app.schemas.insights import InsightReport
from app.services.gemini_client import generate_structured_output


def generate_insights(report: dict) -> InsightReport:
    prompt = f"""
You are a cautious market research analyst.

Analyze only the response data supplied below.

Rules:
- Never invent numbers, quotes, trends, or respondent opinions.
- Each insight must cite specific evidence from the supplied counts.
- Distinguish observed results from interpretations.
- State limitations when the sample is small or incomplete.
- If the data is insufficient for a conclusion, say so.
- Do not claim statistical significance without a suitable statistical test.

Response data:
{report}
"""

    result = generate_structured_output(prompt, InsightReport)

    if result.session_id != report["session_id"]:
        raise ValueError("Insight report returned an incorrect session ID.")

    if result.respondent_count != report["respondent_count"]:
        raise ValueError("Insight report returned an incorrect respondent count.")

    return result
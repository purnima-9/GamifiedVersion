from app.schemas.research_plan import (
    ResearchPlan,
    ResearchConstruct,
    ResearchHypothesis,
)


def get_measurement_method(dimension: str) -> str:
    name = dimension.lower()

    if any(word in name for word in ["price", "pay", "willingness"]):
        return "Price input and price sensitivity"
    if any(word in name for word in ["interest", "intent", "demand"]):
        return "Likert scale and purchase-intent rating"
    if any(word in name for word in ["safety", "trust", "risk"]):
        return "Likert scale and perceived-risk rating"
    if any(word in name for word in ["occasion", "usage", "frequency"]):
        return "Multiple-choice and frequency measurement"
    if any(word in name for word in ["channel", "distribution"]):
        return "Multiple-choice preference measurement"

    return "Likert scale and structured multiple-choice questions"


def generate_research_plan(
    research_id: int,
    topic: str,
    target_audience: str,
    geography: str,
    dimensions: list,
) -> ResearchPlan:
    objectives = [
        f"Measure demand for {topic} among {target_audience}.",
        f"Understand consumer needs and barriers in {geography}.",
        "Identify the factors that influence purchase consideration.",
        "Generate evidence to support product positioning and launch decisions.",
    ]

    constructs = []
    hypotheses = []

    for index, dimension in enumerate(dimensions, start=1):
        name = dimension.name

        constructs.append(
            ResearchConstruct(
                name=name,
                dimension=name,
                measurement_method=get_measurement_method(name),
            )
        )

        hypotheses.append(
            ResearchHypothesis(
                hypothesis_id=f"H{index}",
                statement=(
                    f"{name} is an important factor to investigate "
                    f"when evaluating demand for {topic}."
                ),
                dimension=name,
            )
        )

    return ResearchPlan(
        research_id=research_id,
        research_objectives=objectives,
        constructs=constructs,
        hypotheses=hypotheses,
    )

from app.schemas.research_plan import (
    ResearchPlan,
    ResearchConstruct,
    ResearchHypothesis,
)
from app.schemas.question import (
    SurveyBlueprint,
    SurveyQuestion,
    AnswerOption,
)


def test_llm_planner_validates_output(monkeypatch):
    import app.engines.research_strategies.llm_planner as planner

    fake_plan = ResearchPlan(
        research_id=1,
        research_objectives=["Measure purchase interest"],
        constructs=[
            ResearchConstruct(
                name="Purchase interest",
                dimension="Interest",
                measurement_method="Five-point Likert scale",
            )
        ],
        hypotheses=[
            ResearchHypothesis(
                hypothesis_id="H1",
                statement="Purchase interest varies by respondent.",
                dimension="Interest",
            )
        ],
    )

    monkeypatch.setattr(
        planner,
        "generate_structured_output",
        lambda prompt, model: fake_plan,
    )

    result = planner.generate_research_plan_with_llm(
        research_id=1,
        topic="Self-heating hot chocolate",
        target_audience="Adults aged 18-26",
        geography="India",
        dimensions=["Interest"],
    )

    assert result.research_id == 1
    assert result.constructs[0].dimension == "Interest"


def test_llm_survey_validates_question_ids(monkeypatch):
    import app.engines.survey_architect.llm_architect as architect

    fake_survey = SurveyBlueprint(
        research_id=1,
        title="Hot Chocolate Survey",
        questions=[
            SurveyQuestion(
                question_id="Q001",
                text="Which age group are you in?",
                question_type="single_choice",
                options=[
                    AnswerOption(option_id="A1", label="Under 18"),
                    AnswerOption(option_id="A2", label="18-26"),
                ],
            ),
            SurveyQuestion(
                question_id="Q002",
                text="How interested are you in this product?",
                question_type="likert",
                dimension_mappings={"Interest": 1.0},
                options=[
                    AnswerOption(option_id="A1", label="Not interested"),
                    AnswerOption(option_id="A2", label="Very interested"),
                ],
            ),
        ],
    )

    monkeypatch.setattr(
        architect,
        "generate_structured_output",
        lambda prompt, model: fake_survey,
    )

    result = architect.build_survey_with_llm(
        research_id=1,
        topic="Self-heating hot chocolate",
        dimensions=["Interest"],
        research_plan={"research_objectives": ["Measure interest"]},
    )

    assert len(result.questions) == 2
    assert result.questions[1].dimension_mappings["Interest"] == 1.0
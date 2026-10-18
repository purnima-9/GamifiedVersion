from types import SimpleNamespace

from app.engines.analytics.project_report import build_project_report
from app.schemas.question import (
    AnswerOption,
    SurveyBlueprint,
    SurveyQuestion,
)


def test_project_aggregates_answers_across_sessions():
    blueprint = SurveyBlueprint(
        research_id=1,
        title="Test survey",
        questions=[
            SurveyQuestion(
                question_id="Q001",
                text="Would you buy this?",
                question_type="single_choice",
                options=[
                    AnswerOption(option_id="A1", label="Yes"),
                    AnswerOption(option_id="A2", label="No"),
                ],
            )
        ],
    ).model_dump(mode="json")

    sessions = [
        SimpleNamespace(id=10, status="completed", survey_json=blueprint),
        SimpleNamespace(id=11, status="completed", survey_json=blueprint),
    ]

    answers = [
        SimpleNamespace(
            session_id=10,
            question_id="Q001",
            option_id="A1",
            answer_value=None,
        ),
        SimpleNamespace(
            session_id=11,
            question_id="Q001",
            option_id="A2",
            answer_value=None,
        ),
    ]

    report = build_project_report(1, sessions, answers, [])

    assert report["total_sessions"] == 2
    assert report["eligible_sessions"] == 2
    assert report["completed_sessions"] == 2
    assert report["question_results"][0]["responses"] == 2


def test_project_excludes_ineligible_sessions_from_eligible_count():
    sessions = [
        SimpleNamespace(id=10, status="completed", survey_json=None),
        SimpleNamespace(id=11, status="ineligible", survey_json=None),
    ]

    report = build_project_report(1, sessions, [], [])

    assert report["total_sessions"] == 2
    assert report["eligible_sessions"] == 1
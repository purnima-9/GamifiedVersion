from types import SimpleNamespace

from app.engines.analytics.report import build_session_report
from app.schemas.question import (
    AnswerOption,
    SurveyBlueprint,
    SurveyQuestion,
)


def test_report_counts_answers():
    survey = SurveyBlueprint(
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
    )

    answers = [
        SimpleNamespace(
            session_id=10,
            question_id="Q001",
            option_id="A1",
            answer_value=None,
        ),
        SimpleNamespace(
            session_id=10,
            question_id="Q001",
            option_id="A1",
            answer_value=None,
        ),
    ]

    report = build_session_report(10, survey, answers)

    assert report["answer_count"] == 2
    assert report["question_results"][0]["responses"] == 2
    assert report["question_results"][0]["answer_distribution"][0]["count"] == 2


def test_report_handles_no_answers():
    survey = SurveyBlueprint(
        research_id=1,
        title="Test survey",
        questions=[
            SurveyQuestion(
                question_id="Q001",
                text="Question",
                question_type="likert",
            )
        ],
    )

    report = build_session_report(10, survey, [])

    assert report["answer_count"] == 0
    assert report["question_results"][0]["responses"] == 0
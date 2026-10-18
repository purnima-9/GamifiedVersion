from app.schemas.question import (
    AnswerOption,
    SurveyBlueprint,
    SurveyQuestion,
)


def test_saved_blueprint_round_trip():
    original = SurveyBlueprint(
        research_id=1,
        title="Hot Chocolate Survey",
        questions=[
            SurveyQuestion(
                question_id="Q001",
                text="Select your age group",
                question_type="single_choice",
                options=[
                    AnswerOption(option_id="A1", label="Under 18"),
                    AnswerOption(option_id="A2", label="18-26"),
                ],
            )
        ],
    )

    # Simulate storing the blueprint in SQLite JSON.
    saved_json = original.model_dump(mode="json")
    restored = SurveyBlueprint.model_validate(saved_json)

    assert restored.research_id == original.research_id
    assert restored.questions[0].question_id == "Q001"
    assert restored.questions[0].options[1].option_id == "A2"


def test_saved_blueprint_keeps_question_order():
    blueprint = SurveyBlueprint(
        research_id=1,
        title="Test",
        questions=[
            SurveyQuestion(
                question_id="Q001",
                text="First",
                question_type="likert",
            ),
            SurveyQuestion(
                question_id="Q002",
                text="Second",
                question_type="likert",
            ),
        ],
    )

    restored = SurveyBlueprint.model_validate(
        blueprint.model_dump(mode="json")
    )

    assert [q.question_id for q in restored.questions] == ["Q001", "Q002"]
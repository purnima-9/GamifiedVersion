from types import SimpleNamespace

from app.engines.adaptive.selector import (
    calculate_coverage,
    calculate_target_attainment,
    select_next_question,
)


def make_dimension(name, importance, target):
    return SimpleNamespace(
        name=name,
        importance=importance,
        target_coverage=target,
    )


def make_question(qid, mappings, seconds=10, options=None):
    return SimpleNamespace(
        question_id=qid,
        dimension_mappings=mappings,
        estimated_seconds=seconds,
        options=options or [],
        depends_on=None,
        show_if_option_id=None,
    )


def test_weighted_coverage():
    dimensions = [
        make_dimension("Interest", 10, 0.9),
        make_dimension("Price", 5, 0.8),
    ]

    result = calculate_coverage(
        dimensions, {"Interest": 1.0, "Price": 0.0}
    )

    assert round(result, 2) == 0.67


def test_target_attainment():
    dimensions = [
        make_dimension("Interest", 10, 0.8),
        make_dimension("Price", 5, 0.5),
    ]

    result = calculate_target_attainment(
        dimensions, {"Interest": 0.4, "Price": 0.5}
    )

    assert round(result, 2) == 0.67


def test_selects_unanswered_question():
    dimensions = [make_dimension("Interest", 10, 0.8)]
    questions = [
        make_question("Q1", {"Interest": 1.0}),
        make_question("Q2", {"Interest": 0.5}),
    ]

    selected, _, status = select_next_question(
        questions=questions,
        dimensions=dimensions,
        coverage={},
        answered_ids=["Q1"],
        response_options={},
        asked_count=1,
        max_questions=10,
    )

    assert selected.question_id == "Q2"
    assert status == "question_selected"


def test_stops_at_question_budget():
    selected, scores, status = select_next_question(
        questions=[],
        dimensions=[],
        coverage={},
        answered_ids=[],
        response_options={},
        asked_count=3,
        max_questions=3,
    )

    assert selected is None
    assert scores == []
    assert status == "question_budget_reached"

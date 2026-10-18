from types import SimpleNamespace

from app.engines.adaptive.selector import is_question_eligible


def test_branch_requires_parent_answer():
    question = SimpleNamespace(
        depends_on="Q002",
        show_if_option_id="A1",
    )

    assert not is_question_eligible(question, {})
    assert is_question_eligible(question, {"Q002": "A1"})
    assert not is_question_eligible(question, {"Q002": "A2"})


def test_branch_supports_multiple_choice():
    question = SimpleNamespace(
        depends_on="Q002",
        show_if_option_id="A2",
    )

    assert is_question_eligible(question, {"Q002": ["A1", "A2"]})
    assert not is_question_eligible(question, {"Q002": ["A1"]})


def test_unconditional_question_is_eligible():
    question = SimpleNamespace(
        depends_on=None,
        show_if_option_id=None,
    )

    assert is_question_eligible(question, {})
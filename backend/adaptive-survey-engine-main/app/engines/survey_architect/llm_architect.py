from app.schemas.question import SurveyBlueprint
from app.services.gemini_client import generate_structured_output


def build_survey_with_llm(
    research_id: int,
    topic: str,
    dimensions: list[str],
    research_plan: dict,
    target_audience: str = "Target respondents",
    geography: str = "Not specified",
    max_questions: int = 15,
) -> SurveyBlueprint:

    prompt = f"""
You are a professional survey-methodology expert.

Generate an adaptive survey from the research plan below.

Topic: {topic}
Target audience: {target_audience}
Geography: {geography}
Research dimensions: {dimensions}
Research plan: {research_plan}
Maximum questions: {max_questions}

Question rules:
1. Start with Q001 as an age/eligibility screening question.
2. Use unique, stable question IDs: Q001, Q002, Q003, etc.
3. Use unique option IDs within each question: A1, A2, A3, etc.
4. Supported question types are:
   single_choice, multiple_choice, likert, price_input.
5. Likert questions must have answer options with meaningful labels.
6. Price questions should use price_input and do not require options.
7. Map every research question to one or more supplied dimensions.
8. dimension_mappings must use supplied dimension names and strengths from 0 to 1.
9. For each answer option, dimension_values must use supplied dimension names
   and numeric values from 0 to 1 where applicable.
10. Avoid leading, double-barrelled, repetitive, or ambiguous questions.
11. Include conditional branching when a follow-up is only relevant to an answer.
12. For conditional questions, depends_on must reference an existing question ID
    and show_if_option_id must reference an option on that parent question.
13. Keep the questionnaire concise and suitable for the target audience.
14. Do not invent research findings; this is a questionnaire, not a results report.
15. Include a clear survey title.
"""

    result = generate_structured_output(prompt, SurveyBlueprint)
    result.research_id = research_id

    if not result.questions:
        raise ValueError("Gemini generated a survey with no questions.")

    if len(result.questions) > max_questions:
        raise ValueError(
            f"Generated survey exceeds the limit of {max_questions} questions."
        )

    question_ids = [q.question_id for q in result.questions]
    if len(question_ids) != len(set(question_ids)):
        raise ValueError("Survey contains duplicate question IDs.")

    option_ids_by_question = {}

    for question in result.questions:
        option_ids = [option.option_id for option in question.options]

        if len(option_ids) != len(set(option_ids)):
            raise ValueError(
                f"Duplicate option IDs found in {question.question_id}."
            )

        option_ids_by_question[question.question_id] = set(option_ids)

        unknown_dimensions = (
            set(question.dimension_mappings) - set(dimensions)
        )
        if unknown_dimensions:
            raise ValueError(
                f"{question.question_id} uses unknown dimensions: "
                f"{sorted(unknown_dimensions)}"
            )

        for option in question.options:
            unknown_option_dimensions = (
                set(option.dimension_values) - set(dimensions)
            )
            if unknown_option_dimensions:
                raise ValueError(
                    f"{question.question_id} option {option.option_id} "
                    f"uses unknown dimensions: "
                    f"{sorted(unknown_option_dimensions)}"
                )

    # Validate conditional references after collecting all question IDs.
    for question in result.questions:
        if question.depends_on:
            if question.depends_on not in option_ids_by_question:
                raise ValueError(
                    f"{question.question_id} references an unknown parent question."
                )

            if question.show_if_option_id not in option_ids_by_question[
                question.depends_on
            ]:
                raise ValueError(
                    f"{question.question_id} references an unknown parent option."
                )

    # Validate screening question.
    screening = result.questions[0]

    if screening.question_id != "Q001":
        raise ValueError("The first question must be Q001 screening.")

    if screening.question_type != "single_choice":
        raise ValueError("Q001 must be a single-choice screening question.")

    screening.required = True

    return result
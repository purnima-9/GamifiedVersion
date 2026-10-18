from collections import Counter, defaultdict

from app.schemas.question import SurveyBlueprint


def build_project_report(research_id, sessions, answers, dimensions):
    session_map = {session.id: session for session in sessions}
    question_data = {}
    answer_groups = defaultdict(list)

    for session in sessions:
        if not session.survey_json:
            continue

        survey = SurveyBlueprint.model_validate(session.survey_json)

        for question in survey.questions:
            key = (question.question_id, question.text)
            question_data[key] = {
                "question_id": question.question_id,
                "question": question.text,
                "options": {
                    option.option_id: option.label
                    for option in question.options
                },
            }

    for answer in answers:
        session = session_map.get(answer.session_id)
        if not session or not session.survey_json:
            continue

        survey = SurveyBlueprint.model_validate(session.survey_json)
        question = next(
            (
                q for q in survey.questions
                if q.question_id == answer.question_id
            ),
            None,
        )

        if question:
            key = (question.question_id, question.text)
            answer_groups[key].append(answer)

    question_results = []

    for key, metadata in question_data.items():
        counts = Counter()
        question_answers = answer_groups[key]

        for answer in question_answers:
            if answer.option_id:
                counts[answer.option_id] += 1
            elif isinstance(answer.answer_value, list):
                counts.update(str(value) for value in answer.answer_value)
            elif answer.answer_value is not None:
                counts[str(answer.answer_value)] += 1

        question_results.append({
            "question_id": metadata["question_id"],
            "question": metadata["question"],
            "responses": len(question_answers),
            "answer_distribution": [
                {
                    "answer": metadata["options"].get(value, value),
                    "count": count,
                }
                for value, count in counts.items()
            ],
        })

    eligible_sessions = [
        session for session in sessions
        if session.status != "ineligible"
    ]

    return {
        "research_id": research_id,
        "total_sessions": len(sessions),
        "eligible_sessions": len(eligible_sessions),
        "completed_sessions": sum(
            session.status == "completed"
            for session in sessions
        ),
        "question_results": question_results,
        "dimensions": [
            {
                "name": dimension.name,
                "importance": dimension.importance,
                "target_coverage": dimension.target_coverage,
            }
            for dimension in dimensions
        ],
        "limitations": [
            "Session count is not necessarily the number of unique people.",
            "Question response counts vary because the survey is adaptive.",
            "Results describe collected responses and may not represent the wider population.",
        ],
    }
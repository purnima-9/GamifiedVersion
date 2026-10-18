from collections import Counter, defaultdict


def build_session_report(session_id, survey, answers):
    questions = {q.question_id: q for q in survey.questions}
    grouped = defaultdict(list)

    for answer in answers:
        grouped[answer.question_id].append(answer)

    question_results = []

    for question_id, question in questions.items():
        question_answers = grouped.get(question_id, [])
        counts = Counter()

        for answer in question_answers:
            if answer.option_id:
                counts[answer.option_id] += 1
            elif isinstance(answer.answer_value, list):
                counts.update(map(str, answer.answer_value))
            elif answer.answer_value is not None:
                counts[str(answer.answer_value)] += 1

        option_labels = {
            option.option_id: option.label
            for option in question.options
        }

        question_results.append({
            "question_id": question_id,
            "question": question.text,
            "responses": len(question_answers),
            "answer_distribution": [
                {
                    "answer": option_labels.get(value, value),
                    "count": count,
                }
                for value, count in counts.items()
            ],
        })

    return {
        "session_id": session_id,
        "respondent_count": len({
            answer.session_id for answer in answers
        }),
        "answer_count": len(answers),
        "question_results": question_results,
    }
from math import log2

ALPHA = 0.4  # Expected coverage gain
BETA = 0.3   # Estimated information gain
GAMMA = 0.3  # Relevance


def calculate_coverage(dimensions, current_coverage):
    total_weight = sum(d.importance for d in dimensions)

    if total_weight == 0:
        return 0.0

    return sum(
        d.importance * min(
            max(current_coverage.get(d.name, 0.0), 0.0), 1.0
        )
        for d in dimensions
    ) / total_weight


def calculate_target_attainment(dimensions, current_coverage):
    total_weight = sum(d.importance for d in dimensions)

    if total_weight == 0:
        return 0.0

    attained = 0.0

    for d in dimensions:
        coverage = min(max(current_coverage.get(d.name, 0.0), 0.0), 1.0)
        target = d.target_coverage

        if target <= 0:
            ratio = 1.0
        else:
            ratio = min(coverage / target, 1.0)

        attained += d.importance * ratio

    return attained / total_weight


def score_question(question, dimensions, coverage):
    total_weight = sum(d.importance for d in dimensions)
    if total_weight == 0:
        return None

    dimension_by_name = {d.name: d for d in dimensions}
    mappings = question.dimension_mappings

    # Expected coverage gain, prioritizing important unmet dimensions.
    coverage_gain = 0.0
    denominator = sum(
        d.importance * d.target_coverage for d in dimensions
    )

    if denominator > 0:
        for name, strength in mappings.items():
            d = dimension_by_name.get(name)
            if d is None:
                continue

            current = min(max(coverage.get(name, 0.0), 0.0), 1.0)
            remaining = max(d.target_coverage - current, 0.0)

            coverage_gain += d.importance * strength * remaining

        coverage_gain /= denominator

    # Relevance: importance-weighted strength of mapped dimensions.
    mapped_weight = sum(
        dimension_by_name[name].importance * strength
        for name, strength in mappings.items()
        if name in dimension_by_name
    )

    relevance = min(mapped_weight / total_weight, 1.0)

    # Proxy for information gain. Real IG needs response distributions.
    option_count = len(question.options)
    information_gain = (
        min(log2(option_count) / log2(5), 1.0)
        if option_count > 1
        else 0.5
    )

    base_score = (
        ALPHA * coverage_gain
        + BETA * information_gain
        + GAMMA * relevance
    )

    effort_penalty = 1 + (question.estimated_seconds / 60)

    return {
        "question_id": question.question_id,
        "coverage_gain": round(coverage_gain, 4),
        "estimated_information_gain": round(information_gain, 4),
        "relevance": round(relevance, 4),
        "effort_seconds": question.estimated_seconds,
        "score": round(base_score / effort_penalty, 4),
    }


# def select_next_question(
#     questions,
#     dimensions,
#     coverage,
#     answered_ids,
#     response_options,
#     asked_count,
#     max_questions,
# ):
#     if asked_count >= max_questions:
#         return None, [], "question_budget_reached"

#     candidates = []

#     for question in questions:
#         if question.question_id in answered_ids:
#             continue

#         # Enforce dependencies when configured.
#         if question.depends_on:
#             if question.depends_on not in response_options:
#                 continue

#             if (
#                 question.show_if_option_id
#                 and response_options[question.depends_on]
#                 != question.show_if_option_id
#             ):
#                 continue

#         result = score_question(question, dimensions, coverage)
#         if result is not None:
#             candidates.append((result, question))

#     candidates.sort(key=lambda item: item[0]["score"], reverse=True)

#     if not candidates:
#         return None, [], "no_eligible_questions"

#     best_score, best_question = candidates[0]

#     return (
#         best_question,
#         [score for score, _ in candidates],
#         "question_selected",
#     )

def select_next_question(
    questions,
    dimensions,
    coverage,
    answered_ids,
    response_options,
    asked_count,
    max_questions,
):
    if asked_count >= max_questions:
        return None, [], "question_budget_reached"

    # Filter eligible questions first
    eligible_questions = [
        question
        for question in questions
        if question.question_id not in answered_ids
        and is_question_eligible(question, response_options)
    ]

    candidates = []

    for question in eligible_questions:
        result = score_question(question, dimensions, coverage)
        if result is not None:
            candidates.append((result, question))

    candidates.sort(key=lambda item: item[0]["score"], reverse=True)

    if not candidates:
        return None, [], "no_eligible_questions"

    best_score, best_question = candidates[0]

    return (
        best_question,
        [score for score, _ in candidates],
        "question_selected",
    )

def is_question_eligible(question, response_options: dict) -> bool:
    """Check whether a question's branching condition is satisfied."""

    if not question.depends_on:
        return True

    parent_answer = response_options.get(question.depends_on)

    if parent_answer is None:
        return False

    if isinstance(parent_answer, list):
        return question.show_if_option_id in parent_answer

    return parent_answer == question.show_if_option_id
from app.schemas.question import (
    AnswerOption,
    SurveyQuestion,
    SurveyBlueprint,
)

def make_options(labels: list[str]) -> list[AnswerOption]:
    return [
        AnswerOption(option_id=f"A{index}", label=label)
        for index, label in enumerate(labels, start=1)
    ]


def build_survey(research_id: int, topic: str, dimensions: list) -> SurveyBlueprint:
    questions = []

    # Eligibility question
    questions.append(
        SurveyQuestion(
            question_id="Q001",
            text="Which age group do you belong to?",
            question_type="single_choice",
            required=True,
            options=[
                AnswerOption(option_id="A1", label="Under 18"),
                AnswerOption(option_id="A2", label="18–26"),
                AnswerOption(option_id="A3", label="27–35"),
                AnswerOption(option_id="A4", label="36+"),
            ],
            estimated_seconds=10,
        )
    )

    for index, dimension in enumerate(dimensions, start=2):
        name = dimension.name
        normalized = name.lower()
        question_id = f"Q{index:03d}"

        if any(word in normalized for word in ["price", "pay", "willingness"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"What is the maximum price you would pay for {topic}?",
                question_type="price_input",
                dimension_mappings={name: 1.0},
                required=True,
                estimated_seconds=20,
            )

        elif any(word in normalized for word in ["occasion", "usage", "social"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"When would you most enjoy {topic}?",
                question_type="multiple_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "A relaxing evening",
                    "A morning treat",
                    "A study or work break",
                    "Time with friends or family",
                ]),
                estimated_seconds=15,
            )

        elif "frequency" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How often do you usually drink hot chocolate?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Several times a week",
                    "About once a week",
                    "A few times a month",
                    "Rarely or never",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "flavor" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text=f"Which flavor would you most like to try in {topic}?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Classic chocolate",
                    "Caramel",
                    "Hazelnut",
                    "Mint",
                    "Spiced chocolate",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "sweetness" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How sweet would you like your hot chocolate?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not sweet",
                    "Lightly sweet",
                    "Moderately sweet",
                    "Very sweet",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["milk", "base"]):
            question = SurveyQuestion(
                question_id=question_id,
                text="Which base would you prefer for your hot chocolate?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Dairy milk",
                    "Oat milk",
                    "Almond milk",
                    "Water-based",
                    "No preference",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "topping" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="Which toppings would you add to your hot chocolate?",
                question_type="multiple_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Marshmallows",
                    "Whipped cream",
                    "Chocolate shavings",
                    "Caramel drizzle",
                    "No toppings",
                ]),
                estimated_seconds=15,
            )

        elif "temperature" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How would you like your hot chocolate served?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Hot",
                    "Warm",
                    "Chilled",
                    "No preference",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "size" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="What serving size would you usually choose?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Small cup",
                    "Regular cup",
                    "Large cup",
                    "Sharing size",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["location", "distribution"]):
            question = SurveyQuestion(
                question_id=question_id,
                text="Where would you prefer to buy hot chocolate?",
                question_type="multiple_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Coffee shop or café",
                    "Restaurant",
                    "Grocery or convenience store",
                    "Online delivery",
                ]),
                estimated_seconds=15,
            )

        elif "packaging" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="Which packaging would you prefer for a hot chocolate mix?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Resealable pouch",
                    "Single-serve sachets",
                    "Recyclable carton",
                    "Reusable tin",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["discovery", "channel"]):
            question = SurveyQuestion(
                question_id=question_id,
                text="Where would you most likely discover a new hot chocolate?",
                question_type="multiple_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Social media",
                    "In a café or store",
                    "A recommendation from someone",
                    "Online advertising",
                ]),
                estimated_seconds=15,
            )

        elif "improvement" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="Which change would most improve your hot chocolate experience?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "More flavor choices",
                    "Less sugar",
                    "Better value",
                    "More convenient preparation",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["intent", "demand"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How likely are you to try {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Very unlikely",
                    "Unlikely",
                    "Not sure",
                    "Likely",
                    "Very likely",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "recommend" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How likely are you to recommend {topic} to someone?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Very unlikely",
                    "Unlikely",
                    "Not sure",
                    "Likely",
                    "Very likely",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "sustainability" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How important is sustainable packaging when choosing a hot chocolate?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not important",
                    "Slightly important",
                    "Moderately important",
                    "Very important",
                    "Extremely important",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["interest", "intent", "demand"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How interested are you in trying {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=[
                    AnswerOption(option_id=f"A{i}", label=label)
                    for i, label in enumerate(
                        [
                            "Not at all interested",
                            "Slightly interested",
                            "Moderately interested",
                            "Very interested",
                            "Extremely interested",
                        ],
                        start=1,
                    )
                ],
                required=True,
                estimated_seconds=10,
            )

        elif "trust" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How much do you trust hot chocolate brands to use quality ingredients?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Do not trust at all",
                    "Trust a little",
                    "Neither trust nor distrust",
                    "Trust a lot",
                    "Completely trust",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["safety", "risk"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How concerned are you about the safety of {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not concerned",
                    "Slightly concerned",
                    "Moderately concerned",
                    "Very concerned",
                    "Extremely concerned",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "appeal" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How appealing does {topic} sound to you?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not at all appealing",
                    "Slightly appealing",
                    "Moderately appealing",
                    "Very appealing",
                    "Extremely appealing",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "intensity" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How rich would you like the chocolate flavor to be?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Very light",
                    "Somewhat light",
                    "Just right",
                    "Rich",
                    "Extra rich",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "value" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How important is good value for money when choosing hot chocolate?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not important",
                    "Slightly important",
                    "Moderately important",
                    "Very important",
                    "Extremely important",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "convenience" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="How important is quick and convenient preparation to you?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not important",
                    "Slightly important",
                    "Moderately important",
                    "Very important",
                    "Extremely important",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif "ingredient" in normalized:
            question = SurveyQuestion(
                question_id=question_id,
                text="Which ingredient detail matters most to you?",
                question_type="single_choice",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Real cocoa content",
                    "Natural ingredients",
                    "Low sugar",
                    "No artificial flavors",
                    "Allergen information",
                ]),
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["health", "sugar"]):
            question = SurveyQuestion(
                question_id=question_id,
                text="How important is having a lower-sugar hot chocolate option?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not important",
                    "Slightly important",
                    "Moderately important",
                    "Very important",
                    "Extremely important",
                ]),
                required=True,
                estimated_seconds=10,
            )

        else:
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How important is {name} when choosing {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=make_options([
                    "Not important",
                    "Slightly important",
                    "Moderately important",
                    "Very important",
                    "Extremely important",
                ]),
                required=True,
                estimated_seconds=10,
            )

        questions.append(question)

    return SurveyBlueprint(
        research_id=research_id,
        title=f"{topic} — Research Survey",
        questions=questions,
    )

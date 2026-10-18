import csv
import io
import math
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.database import Base, engine, get_db
from app.schemas.research import ResearchCreate
from app.engines.research_strategies.planner import generate_research_plan
from app.schemas.research_plan import ResearchPlan
from app.engines.survey_architect.architect import build_survey
from app.engines.adaptive.selector import (
    calculate_coverage,
    calculate_target_attainment,
    select_next_question,
)
from app.schemas.adaptive import (
    AdaptiveNextRequest,
    AdaptiveNextResponse,
)
from collections import Counter
from fastapi import Body
from app.schemas.analytics import AnswerSubmission
from fastapi import HTTPException
from app.schemas.llm_requests import (
    LLMResearchPlanRequest,
    LLMSurveyRequest,
)
from app.engines.research_strategies.llm_planner import (
    generate_research_plan_with_llm,
)
from app.engines.survey_architect.llm_architect import (
    build_survey_with_llm,
)
from app.schemas.session_requests import CreateAdaptiveSessionRequest
from app.engines.survey_architect.llm_architect import build_survey_with_llm
from app.schemas.question import SurveyBlueprint
from app.engines.analytics.report import build_session_report
from app.engines.analytics.llm_insights import generate_insights
from app.schemas.question import SurveyBlueprint
from app.db.models import ResearchProject, ResearchDimension, SurveyRun, SurveyAnswer
from app.engines.analytics.project_report import build_project_report
from app.engines.analytics.project_insights import generate_project_insights


load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Adaptive Survey Engine", version="0.1.0")
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "running", "project": "Adaptive Survey Engine"}

@app.post("/api/v1/research", status_code=201)
def create_research(payload: ResearchCreate, db: Session = Depends(get_db)):
    project = ResearchProject(
        topic=payload.topic,
        target_audience=payload.target_audience,
        geography=payload.geography,
        status="created",
    )
    project.dimensions = [
        ResearchDimension(
            name=d.name,
            importance=d.importance,
            target_coverage=d.target_coverage,
        )
        for d in payload.dimensions
    ]
    db.add(project)
    db.commit()
    db.refresh(project)
    return {
        "id": project.id,
        "topic": project.topic,
        "target_audience": project.target_audience,
        "geography": project.geography,
        "status": project.status,
        "dimensions": [
            {"name": d.name, "importance": d.importance,
             "target_coverage": d.target_coverage,
             "achieved_coverage": d.achieved_coverage}
            for d in project.dimensions
        ],
    }

@app.get("/api/v1/research/{research_id}")
def get_research(research_id: int, db: Session = Depends(get_db)):
    project = db.get(ResearchProject, research_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")
    return {
        "id": project.id,
        "topic": project.topic,
        "target_audience": project.target_audience,
        "geography": project.geography,
        "status": project.status,
        "dimensions": [
            {"name": d.name, "importance": d.importance,
             "target_coverage": d.target_coverage,
             "achieved_coverage": d.achieved_coverage}
            for d in project.dimensions
        ],
    }

@app.post(
    "/api/v1/research/{research_id}/plan",
    response_model=ResearchPlan,
)
def create_research_plan(
    research_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(ResearchProject, research_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Research project not found",
        )

    return generate_research_plan(
        research_id=project.id,
        topic=project.topic,
        target_audience=project.target_audience,
        geography=project.geography,
        dimensions=project.dimensions,
    )

@app.post("/api/v1/research/{research_id}/survey")
def generate_survey(research_id: int, db: Session = Depends(get_db)):
    project = db.get(ResearchProject, research_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Research project not found")

    blueprint = build_survey(
        research_id=project.id,
        topic=project.topic,
        dimensions=project.dimensions,
    )

    return blueprint.model_dump()

@app.post(
    "/api/v1/research/{research_id}/adaptive/next",
    response_model=AdaptiveNextResponse,
)
def get_next_adaptive_question(
    research_id: int,
    payload: AdaptiveNextRequest,
    db: Session = Depends(get_db),
):
    project = db.get(ResearchProject, research_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Research project not found",
        )

    blueprint = build_survey(
        research_id=project.id,
        topic=project.topic,
        dimensions=project.dimensions,
    )

    coverage = {
        d.name: min(max(payload.current_coverage.get(d.name, 0.0), 0.0), 1.0)
        for d in project.dimensions
    }

    weighted_coverage = calculate_coverage(project.dimensions, coverage)
    target_attainment = calculate_target_attainment(
        project.dimensions, coverage
    )

    question, scores, status = select_next_question(
        questions=blueprint.questions,
        dimensions=project.dimensions,
        coverage=coverage,
        answered_ids=payload.answered_question_ids,
        response_options=payload.response_options,
        asked_count=payload.asked_count,
        max_questions=payload.max_questions,
    )

    return {
        "status": status,
        "next_question": question.model_dump() if question else None,
        "scores": scores,
        "weighted_coverage": round(weighted_coverage, 4),
        "target_attainment": round(target_attainment, 4),
        "dimension_coverage": coverage,
    }

@app.post("/api/v1/research/{research_id}/sessions")
def start_session(
    research_id: int,
    max_questions: int = 10,
    db: Session = Depends(get_db),
):
    project = db.get(ResearchProject, research_id)

    if not project:
        raise HTTPException(404, "Research project not found")

    if not 1 <= max_questions <= 50:
        raise HTTPException(400, "max_questions must be between 1 and 50")

    blueprint = build_survey(
        research_id=project.id,
        topic=project.topic,
        dimensions=project.dimensions,
    )

    run = SurveyRun(
        project_id=research_id,
        max_questions=max_questions,
        survey_json=blueprint.model_dump(mode="json"),
        served_question_ids=[],
        current_question_id=None,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return {
        "session_id": run.id,
        "research_id": research_id,
        "status": run.status,
        "max_questions": run.max_questions,
        "total_questions": len(blueprint.questions),
    }

# @app.get("/api/v1/sessions/{session_id}/next")
# def next_session_question(
#     session_id: int,
#     db: Session = Depends(get_db),
# ):
#     run = db.get(SurveyRun, session_id)

#     if not run:
#         raise HTTPException(404, "Session not found")

#     if run.status != "active":
#         return {"status": run.status, "next_question": None}

#     project = db.get(ResearchProject, run.project_id)
#     blueprint = build_survey(
#         project.id, project.topic, project.dimensions
#     )

#     answers = db.query(SurveyAnswer).filter_by(
#         session_id=session_id
#     ).all()

#     answered_ids = [a.question_id for a in answers]
#     response_options = {
#         a.question_id: a.option_id
#         for a in answers
#         if a.option_id is not None
#     }

#     # Coverage means the dimension has been measured by an answered question.
#     question_by_id = {q.question_id: q for q in blueprint.questions}
#     coverage = {}

#     for answer in answers:
#         question = question_by_id.get(answer.question_id)
#         if question:
#             for dimension, strength in question.dimension_mappings.items():
#                 coverage[dimension] = max(
#                     coverage.get(dimension, 0.0), strength
#                 )

#     question, scores, status = select_next_question(
#         blueprint.questions,
#         project.dimensions,
#         coverage,
#         answered_ids,
#         response_options,
#         len(answers),
#         run.max_questions,
#     )

#     if question is None:
#         run.status = (
#             "budget_reached"
#             if status == "question_budget_reached"
#             else "completed"
#         )
#         db.commit()

#     return {
#         "status": status,
#         "next_question": question.model_dump() if question else None,
#         "scores": scores,
#         "weighted_coverage": round(
#             calculate_coverage(project.dimensions, coverage), 4
#         ),
#         "target_attainment": round(
#             calculate_target_attainment(project.dimensions, coverage), 4
#         ),
#         "dimension_coverage": coverage,
#     }

@app.get("/api/v1/sessions/{session_id}/next")
def get_next_question(
    session_id: int,
    db: Session = Depends(get_db),
):
    run = db.query(SurveyRun).filter(
        SurveyRun.id == session_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Session not found.")

    if run.status != "active":
        return {
            "status": run.status,
            "next_question": None,
        }

    if not run.survey_json:
        raise HTTPException(
            status_code=409,
            detail="Session has no saved survey blueprint.",
        )

    survey = SurveyBlueprint.model_validate(run.survey_json)
    questions = survey.questions

    answers = (
        db.query(SurveyAnswer)
        .filter(SurveyAnswer.session_id == session_id)
        .all()
    )

    answered_ids = {answer.question_id for answer in answers}

    # Build answer lookup for conditional question routing.
    # response_options = {}

    # for answer in answers:
    #     if answer.option_id:
    #         response_options[answer.question_id] = answer.option_id
    #     elif isinstance(answer.answer_value, list) and answer.answer_value:
    #         response_options[answer.question_id] = answer.answer_value[0]
    #     elif isinstance(answer.answer_value, str):
    #         response_options[answer.question_id] = answer.answer_value

    # This supports both single-choice and multiple-choice branching.
    response_options = {}

    for answer in answers:
        if answer.option_id:
            response_options[answer.question_id] = answer.option_id
        elif isinstance(answer.answer_value, list):
            response_options[answer.question_id] = answer.answer_value
        elif answer.answer_value is not None:
            response_options[answer.question_id] = answer.answer_value

    # Load research dimensions.
    dimensions = (
        db.query(ResearchDimension)
        .filter(ResearchDimension.project_id == run.project_id)
        .all()
    )

    # Calculate dimension coverage from answered questions.
    coverage = {}

    for dimension in dimensions:
        coverage[dimension.name] = 0.0

    question_lookup = {
        question.question_id: question
        for question in questions
    }

    for answer in answers:
        question = question_lookup.get(answer.question_id)

        if question is None:
            continue

        for dimension_name, strength in question.dimension_mappings.items():
            coverage[dimension_name] = max(
                coverage.get(dimension_name, 0.0),
                float(strength),
            )

    weighted_coverage = calculate_coverage(dimensions, coverage)
    target_attainment = calculate_target_attainment(
        dimensions, coverage
    )

    def build_result(status, next_question=None, scores=None):
        return {
            "status": status,
            "next_question": (
                next_question.model_dump()
                if next_question is not None
                else None
            ),
            "scores": scores or [],
            "weighted_coverage": weighted_coverage,
            "target_attainment": target_attainment,
            "dimension_coverage": coverage,
        }

    # Return the same question if the respondent refreshes.
    current_id = run.current_question_id

    if current_id and current_id not in answered_ids:
        current_question = question_lookup.get(current_id)

        if current_question is not None:
            return build_result(
                "question_selected",
                current_question,
            )

    served_ids = list(run.served_question_ids or [])
    served_set = set(served_ids)
    asked_count = len(served_set)

    # Enforce question budget.
    if asked_count >= run.max_questions:
        all_question_ids = {question.question_id for question in questions}
        completed = all_question_ids.issubset(answered_ids)
        run.status = "completed" if completed else "budget_reached"
        run.current_question_id = None
        db.commit()

        return build_result(
            "completed" if completed else "question_budget_reached"
        )

    screening_question = next(
        (question for question in questions if question.question_id == "Q001"),
        None,
    )

    if (
        screening_question is not None
        and screening_question.question_id not in answered_ids
        and screening_question.question_id not in served_set
    ):
        selected, scores, selection_status = (
            screening_question,
            [],
            "question_selected",
        )
    else:
        selected, scores, selection_status = select_next_question(
            questions=questions,
            dimensions=dimensions,
            coverage=coverage,
            answered_ids=list(answered_ids | served_set),
            response_options=response_options,
            asked_count=asked_count,
            max_questions=run.max_questions,
        )

    if selected is None:
        run.status = "completed"
        run.current_question_id = None
        db.commit()

        return build_result("completed", scores=scores)

    run.current_question_id = selected.question_id

    if selected.question_id not in served_set:
        served_ids.append(selected.question_id)
        run.served_question_ids = served_ids

    db.commit()

    return build_result(
        selection_status,
        selected,
        scores,
    )

# v1
# @app.post("/api/v1/sessions/{session_id}/responses")
# def submit_answer(
#     session_id: int,
#     payload: AnswerSubmission,
#     db: Session = Depends(get_db),
# ):
#     run = db.get(SurveyRun, session_id)

#     if not run:
#         raise HTTPException(404, "Session not found")

#     if run.status != "active":
#         raise HTTPException(400, "Session is not active")

#     if db.query(SurveyAnswer).filter_by(
#         session_id=session_id,
#         question_id=payload.question_id,
#     ).first():
#         raise HTTPException(409, "Question already answered")

#     project = db.get(ResearchProject, run.project_id)
#     blueprint = build_survey(
#         project.id, project.topic, project.dimensions
#     )
#     question = next(
#         (q for q in blueprint.questions
#          if q.question_id == payload.question_id),
#         None,
#     )

#     if not question:
#         raise HTTPException(404, "Question not found")

#     if question.question_type in ("single_choice", "likert"):
#         valid_ids = {option.option_id for option in question.options}
#         if payload.option_id not in valid_ids:
#             raise HTTPException(400, "A valid option_id is required")

#     if question.question_type == "multiple_choice":
#         valid_ids = {option.option_id for option in question.options}
#         if (
#             not isinstance(payload.answer_value, list)
#             or not set(payload.answer_value).issubset(valid_ids)
#         ):
#             raise HTTPException(400, "Provide valid option IDs in answer_value")

#     if question.question_type == "price_input":
#         if not isinstance(payload.answer_value, (float, int)):
#             raise HTTPException(400, "A numeric price is required")
#         if payload.answer_value < 0:
#             raise HTTPException(400, "Price cannot be negative")

#     db.add(SurveyAnswer(
#         session_id=session_id,
#         question_id=payload.question_id,
#         option_id=payload.option_id,
#         answer_value=payload.answer_value,
#     ))
#     db.commit()

#     return {
#         "session_id": session_id,
#         "question_id": payload.question_id,
#         "status": "answer_saved",
#     }

# v2
# @app.post("/api/v1/sessions/{session_id}/responses")
# def submit_response(
#     session_id: int,
#     payload: AnswerSubmission,
#     db: Session = Depends(get_db),
# ):
#     run = db.query(SurveyRun).filter(
#         SurveyRun.id == session_id
#     ).first()

#     if not run:
#         raise HTTPException(status_code=404, detail="Session not found.")

#     if run.status != "active":
#         raise HTTPException(
#             status_code=409,
#             detail="Session is not active.",
#         )

#     if not run.survey_json:
#         raise HTTPException(
#             status_code=409,
#             detail="Session has no saved survey blueprint.",
#         )

#     if run.current_question_id != payload.question_id:
#         raise HTTPException(
#             status_code=409,
#             detail="This is not the current question for this session.",
#         )

#     # Prevent duplicate responses.
#     existing_answer = (
#         db.query(SurveyAnswer)
#         .filter(
#             SurveyAnswer.session_id == session_id,
#             SurveyAnswer.question_id == payload.question_id,
#         )
#         .first()
#     )

#     if existing_answer:
#         raise HTTPException(
#             status_code=409,
#             detail="This question has already been answered.",
#         )

#     survey = SurveyBlueprint.model_validate(run.survey_json)

#     question = next(
#         (
#             q for q in survey.questions
#             if q.question_id == payload.question_id
#         ),
#         None,
#     )

#     if question is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Question not found in the saved survey.",
#         )

#     valid_option_ids = {
#         option.option_id for option in question.options
#     }

#     option_id = None
#     answer_value = payload.answer_value

#     # Validate according to question type.
#     if question.question_type in ("single_choice", "likert"):
#         if payload.option_id not in valid_option_ids:
#             raise HTTPException(
#                 status_code=422,
#                 detail="A valid option_id is required.",
#             )

#         option_id = payload.option_id

#     elif question.question_type == "multiple_choice":
#         selected_options = (
#             payload.answer_value
#             if isinstance(payload.answer_value, list)
#             else [payload.option_id] if payload.option_id else []
#         )

#         if not selected_options:
#             raise HTTPException(
#                 status_code=422,
#                 detail="Select at least one option.",
#             )

#         if not all(
#             isinstance(item, str) and item in valid_option_ids
#             for item in selected_options
#         ):
#             raise HTTPException(
#                 status_code=422,
#                 detail="One or more option IDs are invalid.",
#             )

#         if len(selected_options) != len(set(selected_options)):
#             raise HTTPException(
#                 status_code=422,
#                 detail="Duplicate selected options are not allowed.",
#             )

#         answer_value = selected_options

#     elif question.question_type == "price_input":
#         if answer_value is None:
#             raise HTTPException(
#                 status_code=422,
#                 detail="A numeric price is required.",
#             )

#         try:
#             answer_value = float(answer_value)
#         except (TypeError, ValueError) as exc:
#             raise HTTPException(
#                 status_code=422,
#                 detail="Price must be numeric.",
#             ) from exc

#         if not math.isfinite(answer_value) or answer_value < 0:
#             raise HTTPException(
#                 status_code=422,
#                 detail="Price must be a finite, non-negative number.",
#             )

#     # Save the response and clear the current question.
#     answer = SurveyAnswer(
#         session_id=session_id,
#         question_id=payload.question_id,
#         option_id=option_id,
#         answer_value=answer_value,
#     )

#     db.add(answer)
#     run.current_question_id = None

#     try:
#         db.commit()
#     except Exception:
#         db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to save response.",
#         )

#     return {
#         "status": "answer_saved",
#         "session_id": session_id,
#         "question_id": payload.question_id,
#     }

# v3
@app.post("/api/v1/sessions/{session_id}/responses")
def submit_response(
    session_id: int,
    payload: AnswerSubmission,
    db: Session = Depends(get_db),
):
    run = db.query(SurveyRun).filter(
        SurveyRun.id == session_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Session not found.")

    if run.status != "active":
        raise HTTPException(
            status_code=409,
            detail="Session is not active.",
        )

    if not run.survey_json:
        raise HTTPException(
            status_code=409,
            detail="Session has no saved survey blueprint.",
        )

    if run.current_question_id != payload.question_id:
        raise HTTPException(
            status_code=409,
            detail="This is not the current question for this session.",
        )

    # Prevent duplicate responses.
    existing_answer = (
        db.query(SurveyAnswer)
        .filter(
            SurveyAnswer.session_id == session_id,
            SurveyAnswer.question_id == payload.question_id,
        )
        .first()
    )

    if existing_answer:
        raise HTTPException(
            status_code=409,
            detail="This question has already been answered.",
        )

    survey = SurveyBlueprint.model_validate(run.survey_json)

    question = next(
        (
            q for q in survey.questions
            if q.question_id == payload.question_id
        ),
        None,
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found in the saved survey.",
        )

    valid_option_ids = {
        option.option_id for option in question.options
    }

    option_id = None
    answer_value = payload.answer_value

    # Validate according to question type.
    if question.question_type in ("single_choice", "likert"):
        if payload.option_id not in valid_option_ids:
            raise HTTPException(
                status_code=422,
                detail="A valid option_id is required.",
            )

        option_id = payload.option_id

    elif question.question_type == "multiple_choice":
        selected_options = (
            payload.answer_value
            if isinstance(payload.answer_value, list)
            else [payload.option_id] if payload.option_id else []
        )

        if not selected_options:
            raise HTTPException(
                status_code=422,
                detail="Select at least one option.",
            )

        if not all(
            isinstance(item, str) and item in valid_option_ids
            for item in selected_options
        ):
            raise HTTPException(
                status_code=422,
                detail="One or more option IDs are invalid.",
            )

        if len(selected_options) != len(set(selected_options)):
            raise HTTPException(
                status_code=422,
                detail="Duplicate selected options are not allowed.",
            )

        answer_value = selected_options

    elif question.question_type == "price_input":
        if answer_value is None:
            raise HTTPException(
                status_code=422,
                detail="A numeric price is required.",
            )

        try:
            answer_value = float(answer_value)
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail="Price must be numeric.",
            ) from exc

        if not math.isfinite(answer_value) or answer_value < 0:
            raise HTTPException(
                status_code=422,
                detail="Price must be a finite, non-negative number.",
            )

    answer = SurveyAnswer(
        session_id=session_id,
        question_id=payload.question_id,
        option_id=option_id,
        answer_value=answer_value,
    )

    # Detect an ineligible respondent from the age screening question.
    ineligible = False

    if question.question_id == "Q001" and option_id:
        selected_option = next(
            (
                option for option in question.options
                if option.option_id == option_id
            ),
            None,
        )

        if selected_option:
            label = selected_option.label.lower().strip()

            ineligible = any(
                phrase in label
                for phrase in (
                    "under 18",
                    "below 18",
                    "less than 18",
                    "under eighteen",
                    "below eighteen",
                )
            )

    if ineligible:
        run.status = "ineligible"

    run.current_question_id = None
    db.add(answer)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save response.",
        )

    return {
        "status": (
            "ineligible"
            if ineligible
            else "answer_saved"
        ),
        "session_id": session_id,
        "question_id": payload.question_id,
    }

@app.get("/api/v1/sessions/{session_id}/analytics")
def session_analytics(
    session_id: int,
    db: Session = Depends(get_db),
):
    run = db.get(SurveyRun, session_id)

    if not run:
        raise HTTPException(404, "Session not found")

    answers = db.query(SurveyAnswer).filter_by(
        session_id=session_id
    ).all()

    project = db.get(ResearchProject, run.project_id)
    blueprint = build_survey(
        project.id, project.topic, project.dimensions
    )

    question_by_id = {q.question_id: q for q in blueprint.questions}
    coverage = {}

    for answer in answers:
        question = question_by_id.get(answer.question_id)
        if question:
            for dimension, strength in question.dimension_mappings.items():
                coverage[dimension] = max(
                    coverage.get(dimension, 0.0), strength
                )

    answer_counts = {}
    for answer in answers:
        value = answer.option_id or str(answer.answer_value)
        answer_counts.setdefault(answer.question_id, Counter())[value] += 1

    return {
        "session_id": session_id,
        "status": run.status,
        "questions_answered": len(answers),
        "weighted_coverage": round(
            calculate_coverage(project.dimensions, coverage), 4
        ),
        "target_attainment": round(
            calculate_target_attainment(project.dimensions, coverage), 4
        ),
        "dimension_coverage": coverage,
        "answer_counts": {
            qid: dict(counts) for qid, counts in answer_counts.items()
        },
    }

@app.post("/api/v1/llm/research-plan")
def create_llm_research_plan(payload: LLMResearchPlanRequest):
    try:
        plan = generate_research_plan_with_llm(
            research_id=payload.research_id,
            topic=payload.topic,
            target_audience=payload.target_audience,
            geography=payload.geography,
            dimensions=payload.dimensions,
        )
        return plan.model_dump()

    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/v1/llm/survey")
def create_llm_survey(payload: LLMSurveyRequest):
    try:
        survey = build_survey_with_llm(
            research_id=payload.research_id,
            topic=payload.topic,
            dimensions=payload.dimensions,
            research_plan=payload.research_plan,
            target_audience=payload.target_audience,
            geography=payload.geography,
            max_questions=payload.max_questions,
        )
        return survey.model_dump()

    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/v1/llm/sessions")
def create_llm_session(
    payload: CreateAdaptiveSessionRequest,
    db: Session = Depends(get_db),
):
    survey = build_survey_with_llm(
        research_id=payload.research_id,
        topic=payload.topic,
        dimensions=payload.dimensions,
        research_plan=payload.research_plan,
        target_audience=payload.target_audience,
        geography=payload.geography,
        max_questions=payload.max_questions,
    )

    run = SurveyRun(
        project_id=payload.research_id,
        status="active",
        max_questions=payload.max_questions,
        survey_json=survey.model_dump(mode="json"),
        served_question_ids=[],
        current_question_id=None,
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return {
        "session_id": run.id,
        "research_id": payload.research_id,
        "status": run.status,
        "question_budget": run.max_questions,
        "survey_title": survey.title,
        "total_questions": len(survey.questions),
    }

@app.get("/api/v1/sessions/{session_id}/report")
def get_session_report(
    session_id: int,
    db: Session = Depends(get_db),
):
    run = db.query(SurveyRun).filter(
        SurveyRun.id == session_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not run.survey_json:
        raise HTTPException(
            status_code=409,
            detail="Session has no saved survey blueprint.",
        )

    answers = db.query(SurveyAnswer).filter(
        SurveyAnswer.session_id == session_id
    ).all()

    survey = SurveyBlueprint.model_validate(run.survey_json)

    return build_session_report(session_id, survey, answers)


@app.get("/api/v1/sessions/{session_id}/export.csv")
def export_session_csv(
    session_id: int,
    db: Session = Depends(get_db),
):
    run = db.query(SurveyRun).filter(
        SurveyRun.id == session_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Session not found.")

    answers = db.query(SurveyAnswer).filter(
        SurveyAnswer.session_id == session_id
    ).all()

    survey = SurveyBlueprint.model_validate(run.survey_json)
    questions = {q.question_id: q for q in survey.questions}

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "session_id",
        "question_id",
        "question",
        "option_id",
        "answer_value",
    ])

    for answer in answers:
        question = questions.get(answer.question_id)

        writer.writerow([
            session_id,
            answer.question_id,
            question.text if question else "",
            answer.option_id or "",
            answer.answer_value
            if isinstance(answer.answer_value, (str, int, float))
            else str(answer.answer_value or ""),
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="survey_session_{session_id}.csv"'
            )
        },
    )


@app.post("/api/v1/sessions/{session_id}/insights")
def get_session_insights(
    session_id: int,
    db: Session = Depends(get_db),
):
    run = db.query(SurveyRun).filter(
        SurveyRun.id == session_id
    ).first()

    if not run:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not run.survey_json:
        raise HTTPException(
            status_code=409,
            detail="Session has no saved survey blueprint.",
        )

    answers = db.query(SurveyAnswer).filter(
        SurveyAnswer.session_id == session_id
    ).all()

    survey = SurveyBlueprint.model_validate(run.survey_json)
    report = build_session_report(session_id, survey, answers)

    if not answers:
        raise HTTPException(
            status_code=422,
            detail="No responses are available to analyze.",
        )

    try:
        return generate_insights(report).model_dump()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/v1/research/{research_id}/analytics")
def get_project_analytics(
    research_id: int,
    db: Session = Depends(get_db),
):
    project = db.query(ResearchProject).filter(
        ResearchProject.id == research_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Research project not found.")

    sessions = db.query(SurveyRun).filter(
        SurveyRun.project_id == research_id
    ).all()

    session_ids = [session.id for session in sessions]

    answers = (
        db.query(SurveyAnswer)
        .filter(SurveyAnswer.session_id.in_(session_ids))
        .all()
        if session_ids
        else []
    )

    dimensions = db.query(ResearchDimension).filter(
        ResearchDimension.project_id == research_id
    ).all()

    return build_project_report(
        research_id=research_id,
        sessions=sessions,
        answers=answers,
        dimensions=dimensions,
    )

@app.get("/api/v1/research/{research_id}/export.csv")
def export_project_analytics(
    research_id: int,
    db: Session = Depends(get_db),
):
    report = get_project_analytics(research_id, db)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "research_id",
        "question_id",
        "question",
        "responses",
        "answer",
        "count",
    ])

    for item in report["question_results"]:
        if not item["answer_distribution"]:
            writer.writerow([
                research_id,
                item["question_id"],
                item["question"],
                item["responses"],
                "",
                0,
            ])
            continue

        for distribution in item["answer_distribution"]:
            writer.writerow([
                research_id,
                item["question_id"],
                item["question"],
                item["responses"],
                distribution["answer"],
                distribution["count"],
            ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="research_{research_id}_analytics.csv"'
            )
        },
    )

@app.post("/api/v1/research/{research_id}/insights")
def get_project_insights(
    research_id: int,
    db: Session = Depends(get_db),
):
    report = get_project_analytics(research_id, db)

    if report["eligible_sessions"] == 0:
        raise HTTPException(
            status_code=422,
            detail="No eligible respondent sessions are available.",
        )

    try:
        return generate_project_insights(report).model_dump()
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
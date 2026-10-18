import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_project(client):
    response = client.post(
        "/api/v1/research",
        json={
            "topic": "Premium hot chocolate",
            "target_audience": "Adults",
            "geography": "India",
            "dimensions": [
                {
                    "name": "Purchase intent",
                    "importance": 8,
                    "target_coverage": 0.8,
                }
            ],
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_hot_chocolate_configuration_creates_25_question_survey(client):
    dimensions = [
        "Overall appeal",
        "Consumption occasions",
        "Flavor preferences",
        "Sweetness preference",
        "Cocoa intensity preference",
        "Milk and base preference",
        "Topping preferences",
        "Serving temperature",
        "Serving size preference",
        "Purchase frequency",
        "Purchase intent",
        "Price willingness",
        "Value for money",
        "Preferred purchase location",
        "Product convenience",
        "Ingredient expectations",
        "Sugar and health perception",
        "Brand trust",
        "Packaging preference",
        "Sustainability importance",
        "Sharing and social occasions",
        "Product discovery channel",
        "Likelihood to recommend",
        "Product improvements",
    ]
    project_response = client.post(
        "/api/v1/research",
        json={
            "topic": "Premium hot chocolate",
            "target_audience": "Hot chocolate consumers aged 18 and above",
            "geography": "India",
            "dimensions": [
                {
                    "name": name,
                    "importance": 7,
                    "target_coverage": 0.75,
                }
                for name in dimensions
            ],
        },
    )
    assert project_response.status_code == 201
    research_id = project_response.json()["id"]

    session_response = client.post(
        f"/api/v1/research/{research_id}/sessions?max_questions=25"
    )
    assert session_response.status_code == 200
    assert session_response.json()["total_questions"] == 25
    session_id = session_response.json()["session_id"]

    question = client.get(
        f"/api/v1/sessions/{session_id}/next"
    ).json()["next_question"]
    asked_count = 0

    while question is not None:
        asked_count += 1
        if question["question_id"] == "Q001":
            answer = {"option_id": "A2"}
        elif question["question_type"] == "price_input":
            answer = {"answer_value": 149}
        elif question["question_type"] == "multiple_choice":
            answer = {"answer_value": ["A1", "A2"]}
        else:
            assert question["options"]
            answer = {"option_id": question["options"][0]["option_id"]}

        response = client.post(
            f"/api/v1/sessions/{session_id}/responses",
            json={"question_id": question["question_id"], **answer},
        )
        assert response.status_code == 200
        next_result = client.get(
            f"/api/v1/sessions/{session_id}/next"
        ).json()
        question = next_result["next_question"]

    assert asked_count == 25
    assert next_result["status"] == "completed"


def test_session_persists_blueprint_and_serves_adaptive_questions(client):
    research_id = create_project(client)
    session_response = client.post(
        f"/api/v1/research/{research_id}/sessions?max_questions=5"
    )

    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    assert session_response.json()["total_questions"] == 2

    screening = client.get(f"/api/v1/sessions/{session_id}/next").json()
    assert screening["next_question"]["question_id"] == "Q001"

    answer = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        json={"question_id": "Q001", "option_id": "A2"},
    )
    assert answer.status_code == 200

    next_question = client.get(
        f"/api/v1/sessions/{session_id}/next"
    ).json()
    assert next_question["next_question"]["question_id"] == "Q002"

    answer = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        json={"question_id": "Q002", "option_id": "A4"},
    )
    assert answer.status_code == 200

    completed = client.get(f"/api/v1/sessions/{session_id}/next").json()
    assert completed["status"] == "completed"
    assert completed["next_question"] is None


def test_underage_screening_ends_the_session(client):
    research_id = create_project(client)
    session = client.post(
        f"/api/v1/research/{research_id}/sessions?max_questions=5"
    ).json()
    session_id = session["session_id"]

    client.get(f"/api/v1/sessions/{session_id}/next")
    response = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        json={"question_id": "Q001", "option_id": "A1"},
    )
    assert response.json()["status"] == "ineligible"

    next_question = client.get(
        f"/api/v1/sessions/{session_id}/next"
    ).json()
    assert next_question == {"status": "ineligible", "next_question": None}


@pytest.mark.parametrize(
    ("dimension", "expected_type", "answer_payload"),
    [
        (
            "Consumption occasions",
            "multiple_choice",
            {"answer_value": ["A1", "A3"]},
        ),
        (
            "Price willingness",
            "price_input",
            {"answer_value": 149.5},
        ),
    ],
)
def test_session_accepts_adaptive_answer_types(
    client,
    dimension,
    expected_type,
    answer_payload,
):
    project_response = client.post(
        "/api/v1/research",
        json={
            "topic": "Premium hot chocolate",
            "target_audience": "Adults",
            "geography": "India",
            "dimensions": [
                {
                    "name": dimension,
                    "importance": 8,
                    "target_coverage": 0.8,
                }
            ],
        },
    )
    research_id = project_response.json()["id"]
    session = client.post(
        f"/api/v1/research/{research_id}/sessions?max_questions=5"
    ).json()
    session_id = session["session_id"]

    client.get(f"/api/v1/sessions/{session_id}/next")
    client.post(
        f"/api/v1/sessions/{session_id}/responses",
        json={"question_id": "Q001", "option_id": "A2"},
    )
    question = client.get(
        f"/api/v1/sessions/{session_id}/next"
    ).json()["next_question"]
    assert question["question_type"] == expected_type

    answer = client.post(
        f"/api/v1/sessions/{session_id}/responses",
        json={"question_id": question["question_id"], **answer_payload},
    )
    assert answer.status_code == 200
    assert client.get(
        f"/api/v1/sessions/{session_id}/next"
    ).json()["status"] == "completed"

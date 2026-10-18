import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, ValidationError

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def generate_structured_output(
    prompt: str,
    output_model: type[BaseModel],
) -> BaseModel:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
            "response_json_schema": output_model.model_json_schema(),
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    try:
        return output_model.model_validate_json(response.text)
    except ValidationError as exc:
        raise ValueError(
            f"Gemini output failed {output_model.__name__} validation."
        ) from exc
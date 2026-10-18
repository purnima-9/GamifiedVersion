from pydantic import BaseModel


class AnswerSubmission(BaseModel):
    question_id: str
    option_id: str | None = None
    answer_value: str | float | int | list[str] | None = None
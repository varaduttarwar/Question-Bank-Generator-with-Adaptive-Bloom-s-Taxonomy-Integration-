from pydantic import BaseModel

class Question(BaseModel):
    subject: str
    syllabus: str
    question: str
    answer: str
    difficulty: str
    question_type: str
    bloom_level: str

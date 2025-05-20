import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.question_generator import generate_questions, generate_quiz
from backend.document_processor import extract_text_from_document

__all__ = ["generate_questions", "generate_quiz", "extract_text_from_document"]

from backend.database import save_question

sample_questions = [
    {"subject": "Math", "syllabus": "Algebra", "question": "What is 2+2?", "answer": "4", "difficulty": "Easy", "bloom_level": "Understanding"}
]

for q in sample_questions:
    save_question(q)

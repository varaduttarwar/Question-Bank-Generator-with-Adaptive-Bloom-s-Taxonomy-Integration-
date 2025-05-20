from backend.database import save_quiz_result

def process_quiz_submission(user_answers):
    """
    Evaluates the quiz submission.

    Args:
        user_answers (dict): {question_id: selected_answer}

    Returns:
        dict: {"score": int, "total": int, "results": list}
    """
    from backend.database import get_questions
    
    # Fetch all questions from DB (or optimize to fetch only required ones)
    all_questions = get_questions()
    question_map = {q["id"]: q["answer"] for q in all_questions}

    score = 0
    results = []

    for qid, user_ans in user_answers.items():
        correct_ans = question_map.get(qid, "").strip()
        is_correct = user_ans.strip().lower() == correct_ans.lower()
        score += 1 if is_correct else 0
        
        results.append({
            "question_id": qid,
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct
        })

    return {"score": score, "total": len(user_answers), "results": results}

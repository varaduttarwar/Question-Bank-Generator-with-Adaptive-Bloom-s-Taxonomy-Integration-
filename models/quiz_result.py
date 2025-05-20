class QuizResult:
    """
    A model representing a quiz result.

    Attributes:
        user_id (str): The unique identifier for the user.
        quiz_id (str): The unique identifier for the quiz.
        score (int): The number of correct answers.
        total_questions (int): The total number of questions.
        percentage (float): The quiz score percentage.
    """
    def __init__(self, user_id, quiz_id, score, total_questions):
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.score = score
        self.total_questions = total_questions
        self.percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    def to_dict(self):
        """ Convert the QuizResult object to a dictionary. """
        return {
            "user_id": self.user_id,
            "quiz_id": self.quiz_id,
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": self.percentage
        }

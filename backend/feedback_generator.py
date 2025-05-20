import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM with API Key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Error: GROQ_API_KEY is not set. Please check your .env file!")

llm = ChatGroq(temperature=0.5, groq_api_key=groq_api_key, model_name="llama3-8b-8192")

def generate_feedback(question, user_answer, correct_answer):
    """
    Uses AI to generate feedback on the user's answer.

    Args:
        question (str): The quiz question.
        user_answer (str): The user's submitted answer.
        correct_answer (str): The expected correct answer.

    Returns:
        str: AI-generated feedback.
    """
    prompt = f"""
    Question: {question}
    User Answer: {user_answer}
    Correct Answer: {correct_answer}
    
    Provide detailed feedback on whether the user’s answer is correct or incorrect. If incorrect, explain why and provide hints.
    """
    
    response = llm.invoke(prompt).content.strip()
    
    return response

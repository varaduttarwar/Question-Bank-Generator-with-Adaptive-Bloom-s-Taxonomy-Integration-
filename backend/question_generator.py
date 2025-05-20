import os
import re
from database import get_db_connection
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from backend.database import get_questions, insert_question

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Error: GROQ_API_KEY is not set. Please check your .env file!")

# Initialize Language Model
llm = ChatGroq(temperature=0.5, groq_api_key=groq_api_key, model_name="llama3-8b-8192")

def generate_questions(subject_name, syllabus, num_questions, example_questions,
                     difficulty, question_type, q_format, bloom_level,
                     include_answers, marks_weightage):
    few_shot_examples = "\n".join([f"Example {i+1}: {q}" for i, q in enumerate(example_questions)])
    
    # Enhanced MCQ instruction
    mcq_instruction = ""
    if q_format.lower() == "mcq":
        mcq_instruction = """
        For multiple choice questions:
        - Generate exactly 4 options labeled a), b), c), d)
        - Mark the correct answer with '(Correct)' after the option text
        - Format example:
          Q1: What is 2+2?
          a) 3
          b) 4 (Correct)
          c) 5
          d) 6
        """

    prompt_template = f"""
    Generate exactly {num_questions} {q_format} questions for {subject_name}.
    Syllabus: {syllabus}
    Difficulty: {difficulty}
    Bloom's Level: {bloom_level}
    {mcq_instruction}
    {f"Include detailed answers (weight: {marks_weightage} marks)" if include_answers else ""}

    Examples:
    {few_shot_examples}

    Format each question as:
    Q{{number}}: <question>
    {"" if q_format.lower() != "mcq" else "a) <option1>\nb) <option2>\nc) <option3>\nd) <option4>"}
    {"" if not include_answers else "Answer: <correct answer>"}
    """

    response = llm.invoke(prompt_template).content.strip()
    
    # Debug output to console
    print("\n=== FULL GENERATED OUTPUT ===")
    print(response)
    print("===========================\n")

    # Process response
    questions = []
    
    if q_format.lower() == "mcq":
        # Pattern to match MCQ questions with options
        pattern = r"Q(\d+): (.+?)\na\) (.+?)\nb\) (.+?)\nc\) (.+?)\nd\) (.+?)(?:\n|$)"
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches:
            q_num, question, opt_a, opt_b, opt_c, opt_d = match
            
            # Find correct answer (marked with (Correct))
            correct_answer = ""
            options = [opt_a, opt_b, opt_c, opt_d]
            for opt in options:
                if "(Correct)" in opt:
                    correct_answer = opt.replace("(Correct)", "").strip()
                    break
            
            # Clean options by removing (Correct) marker
            clean_options = [opt.replace("(Correct)", "").strip() for opt in options]
            
            # Format question with options as part of the text
            question_with_options = f"{question}\n\nOptions:\n"
            question_with_options += "\n".join([f"{chr(97+i)}) {opt}" for i, opt in enumerate(clean_options)])
            
            question_data = {
                "id": int(q_num),
                "question": question_with_options,
                "type": "mcq",
                "correct_answer": correct_answer,
                "user_answer": None
            }
            questions.append(question_data)
            
            # Console debug output
            print(f"Q{q_num}: {question}")
            for i, opt in enumerate(clean_options):
                print(f"{chr(97+i)}) {opt}{' (Correct)' if opt == correct_answer else ''}")
            print(f"Correct Answer: {correct_answer}\n")
    else:
        # Pattern for short/long answer questions
        pattern = r"Q(\d+):\s*(.+?)\nAnswer:\s*(.+?)(?=\nQ|\n\n|$)"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if not matches and include_answers:
            # Fallback pattern if first one doesn't match
            pattern = r"Q(\d+):\s*(.+?)\n(?:Answer|Ans):\s*(.+?)(?=\nQ|\n\n|$)"
            matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches:
            q_num, question, answer = match
            question_data = {
                "id": int(q_num),
                "question": question.strip(),
                "type": q_format.lower(),
                "correct_answer": answer.strip(),
                "user_answer": None
            }
            questions.append(question_data)
            print(f"Q{q_num}: {question.strip()}")
            print(f"Answer: {answer.strip()}\n")
            
        # Handle case where no answers were extracted but questions exist
        if not matches:
            # Fallback to extract just questions
            pattern = r"Q(\d+):\s*(.+?)(?=\nQ|\n\n|$)"
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                q_num, question = match
                question_data = {
                    "id": int(q_num),
                    "question": question.strip(),
                    "type": q_format.lower(),
                    "correct_answer": "",
                    "user_answer": None
                }
                questions.append(question_data)
                print(f"Q{q_num}: {question.strip()}")
                print("Answer: [Not extracted]\n")

    return questions

def generate_quiz(subject, question_type, num_questions, difficulty):
    """Generate quiz questions with proper error handling"""
    try:
        # Use get_questions from database.py
        questions = get_questions(subject, question_type, difficulty, num_questions)
        
        if not questions:
            st.warning(f"No questions found for {subject} with type {question_type} and difficulty {difficulty}")
            return []
        
        # Format questions consistently
        formatted_questions = []
        for idx, q in enumerate(questions, 1):
            formatted_q = {
                "id": idx,
                "question": q["question"],
                "question_type": q["question_type"],
                "difficulty": q["difficulty"],
                "correct_answer": q["answer"]
            }
            formatted_questions.append(formatted_q)
        
        return formatted_questions
        
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return []
import sys
import os
import streamlit as st
import json
import PyPDF2
import traceback
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(temperature=0.5, groq_api_key=groq_api_key, model_name="llama3-8b-8192")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.quiz_manager import process_quiz_submission
from backend.question_generator import generate_quiz, generate_questions
from backend.feedback_generator import generate_feedback
from backend.database import insert_question

st.title("Exam & Quiz System")

def display_generated_questions():
    if "questions_with_answers" in st.session_state:
        st.subheader("Generated Questions")
        
        for q in st.session_state.questions_with_answers:
            with st.expander(f"Q{q['id']}", expanded=False):
                st.markdown(q["question"])
                if st.session_state.include_answers and q.get("correct_answer"):
                    st.markdown(f"Correct Answer: {q['correct_answer']}")

def display_quiz_results():
    """Display quiz results after submission"""
    st.subheader("Quiz Results")
    
    quiz_data = st.session_state.quiz
    score = 0
    
    for q in quiz_data['questions']:
        user_answer = quiz_data['answers'].get(str(q['id']))
        correct_answer = q.get('correct_answer', "No correct answer provided")
        
        is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
        if is_correct:
            score += 1
        
        with st.expander(f"Question {q['id']}", expanded=False):
            st.markdown(q['question'])
            st.markdown(f"Your answer: {user_answer if user_answer is not None else 'No answer provided'}")
            st.markdown(f"Correct answer: {correct_answer}")
            if is_correct:
                st.success("Correct!")
            else:
                st.error("Incorrect")
    
    st.success(f"Final Score: {score}/{len(quiz_data['questions'])}")
    
    if st.button("Start New Quiz"):
        st.session_state.clear()
        st.rerun()

def parse_quiz(response):
    try:
        response_text = response.content if hasattr(response, "content") else str(response)
        response_text = response_text.strip().strip("json").strip("").strip()
        quiz_data = json.loads(response_text)

        if isinstance(quiz_data, list):
            for q in quiz_data:
                if 'correct_answer' in q and 'options' in q:
                    if len(q['correct_answer']) == 1 and q['correct_answer'].isalpha():
                        index = ord(q['correct_answer'].upper()) - ord('A')
                        if 0 <= index < len(q['options']):
                            q['correct_answer'] = q['options'][index]
            
            return quiz_data
        else:
            raise ValueError("Invalid quiz structure")

    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Failed to parse the generated quiz. Error: {str(e)}")
        return None

def generate_quiz_from_pdf(text, number, subject, tone):
    quiz_prompt = PromptTemplate(
        input_variables=["text", "number", "subject", "tone"],
        template=(
            "You are an expert in creating MCQ quizzes.\n"
            "Generate {number} multiple-choice questions for {subject} students in a {tone} tone.\n"
            "Return only JSON with this structure:\n"
            "[\n"
            "  {{ 'question': '...', 'options': ['...', '...', '...', '...'], 'correct_answer': '...' }}\n"
            "]\n\n"
            "Ensure 'correct_answer' matches exactly one of the options.\n"
            "Return ONLY the JSON output without any extra text.\n\n"
            "Text:\n{text}"
        )
    )

    quiz_chain = quiz_prompt | llm | RunnableLambda(parse_quiz)
    return quiz_chain.invoke({"text": text, "number": number, "subject": subject, "tone": tone})

# Initialize session state
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "include_answers" not in st.session_state:
    st.session_state.include_answers = False

# Sidebar mode selection
mode = st.sidebar.radio("Choose Mode", ["Generate Questions", "Take Quiz", "Upload PDF"])

# ========== Generate Questions Mode ==========
if mode == "Generate Questions":
    # Sidebar Inputs
    subject_name = st.sidebar.text_input("Subject Name", "Computer Networks")
    syllabus = st.sidebar.text_area("Syllabus", "TCP Protocol, Three-way Handshake, Checksum")
    num_questions = st.sidebar.slider("Number of Questions", 1, 100, 3)
    difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    q_format = st.sidebar.selectbox("Question Format", ["MCQ", "Short Answer", "True/False"])
    st.session_state.include_answers = st.sidebar.checkbox("Include Answers?", True)
    marks_weightage = st.sidebar.slider("Marks Weightage (1-10)", 1, 10, 5)
    example_questions = st.sidebar.text_area("Example Questions (one per line)", "What is TCP?\nExplain three-way handshake").split("\n")
    bloom_level = st.sidebar.selectbox(
        "Bloom's Taxonomy Level", ["Remembering", "Understanding", "Applying", "Analyzing", "Evaluating", "Creating"]
    )

    if st.sidebar.button("Generate Questions"):
        if subject_name and syllabus:
            with st.spinner("Generating questions..."):
                try:
                    questions = generate_questions(
                        subject_name, syllabus, num_questions, example_questions,
                        difficulty, "Conceptual", q_format, bloom_level, 
                        st.session_state.include_answers, marks_weightage
                    )
                    
                    if questions:
                        st.session_state.questions_with_answers = questions
                        st.success(f"Generated {len(questions)} questions!")
                        
                        # Store in database
                        for q in questions:
                            try:
                                answer = q.get('correct_answer', '').strip()
                                
                                insert_question(
                                    subject=subject_name,
                                    question=q['question'].strip(),
                                    answer=answer,
                                    difficulty=difficulty,
                                    question_type=q_format,
                                    bloom_level=bloom_level
                                )
                                print(f"✅ Inserted question: {q['question']} with answer: {answer}")
                            except Exception as e:
                                st.error(f"Error saving question: {str(e)}")
                                print(f"❌ Error saving question: {str(e)}")
                                continue
                    else:
                        st.error("No questions were generated. Please try different parameters.")
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")
                    print(f"❌ Error generating questions: {str(e)}")

    # Display questions with answers
    if "questions_with_answers" in st.session_state and st.session_state.questions_with_answers:
        display_generated_questions()

# ========== Take Quiz Mode ==========
elif mode == "Take Quiz":
    st.sidebar.header("Quiz Settings")
    
    subject_name = st.sidebar.text_input("Subject Name", "Computer Networks")
    question_type = st.sidebar.selectbox(
        "Question Type", 
        ["MCQ", "Short Answer", "True/False"],
        index=0
    )
    difficulty = st.sidebar.selectbox(
        "Difficulty Level", 
        ["Easy", "Medium", "Hard"],
        index=1
    )
    num_questions = st.sidebar.slider(
        "Number of Questions", 
        1, 20, 3
    )

    if 'quiz' not in st.session_state:
        st.session_state.quiz = {
            'started': False,
            'current_index': 0,
            'answers': {},
            'questions': []
        }

    if st.sidebar.button("Start Quiz") and not st.session_state.quiz['started']:
        with st.spinner("Preparing your quiz..."):
            try:
                quiz_questions = generate_quiz(
                    subject_name,
                    question_type,
                    num_questions,
                    difficulty
                )
                
                if quiz_questions:
                    st.session_state.quiz = {
                        'started': True,
                        'current_index': 0,
                        'answers': {str(q.get('id', idx)): None for idx, q in enumerate(quiz_questions)},
                        'questions': quiz_questions
                    }
                else:
                    st.error("Could not generate quiz. Please try different parameters.")
            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")

    if st.session_state.quiz.get('started'):
        try:
            current_idx = st.session_state.quiz['current_index']
            questions = st.session_state.quiz['questions']
            current_q = questions[current_idx]
            
            st.subheader(f"Question {current_idx + 1} of {len(questions)}")
            st.markdown(current_q.get('question'))
            
            # Handle different question types
            if question_type == "MCQ" and 'options' in current_q:
                # Display as radio buttons for MCQs
                options = current_q['options']
                answer = st.radio(
                    "Select your answer:",
                    options,
                    key=f"q_{current_q.get('id', current_idx)}",
                    index=None
                )
            elif question_type == "True/False":
                # Display as radio buttons for True/False
                answer = st.radio(
                    "Select your answer:",
                    ["True", "False"],
                    key=f"q_{current_q.get('id', current_idx)}",
                    index=None
                )
            else:
                # Display as text input for short answers
                answer = st.text_input(
                    "Your answer:",
                    key=f"q_{current_q.get('id', current_idx)}"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if current_idx > 0 and st.button("Previous"):
                    st.session_state.quiz['answers'][str(current_q.get('id', current_idx))] = answer
                    st.session_state.quiz['current_index'] -= 1
                    st.rerun()
            
            with col2:
                if current_idx < len(questions) - 1:
                    if st.button("Next"):
                        st.session_state.quiz['answers'][str(current_q.get('id', current_idx))] = answer
                        st.session_state.quiz['current_index'] += 1
                        st.rerun()
                else:
                    if st.button("Submit Quiz"):
                        st.session_state.quiz['answers'][str(current_q.get('id', current_idx))] = answer
                        st.session_state.quiz_completed = True
                        st.rerun()
        except Exception as e:
            st.error(f"Error displaying question: {str(e)}")

    if st.session_state.get('quiz_completed'):
        display_quiz_results()

# ========== Upload PDF Mode ==========
elif mode == "Upload PDF":
    st.header("Generate and Take Quiz from PDF")
    
    uploaded_file = st.file_uploader("Upload a PDF or text file", type=["pdf", "txt"])
    text = ""  # Initialize text variable
    
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            text = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                st.error("Failed to extract text from PDF. Please try another file.")
                st.stop()
        
        if not text.strip():
            st.error("The uploaded file is empty or could not be processed.")
            st.stop()
        
        number = st.number_input("Number of MCQs", min_value=1, value=5)
        subject = st.text_input("Subject", "Computer Networks")
        tone = st.selectbox("Tone", ["Easy", "Medium", "Hard"])
        
        if st.button("Generate Quiz from PDF"):
            try:
                quiz = generate_quiz_from_pdf(text, number, subject, tone)
                if not quiz:
                    st.error("Failed to generate quiz from PDF content")
                    st.stop()
                
                # Store in database
                for q in quiz:
                    try:
                        insert_question(
                            subject=subject,
                            question=q['question'],
                            answer=q['correct_answer'],
                            difficulty=tone,
                            question_type="MCQ",
                            bloom_level="Remembering"
                        )
                    except Exception as e:
                        st.error(f"Error saving question: {str(e)}")
                        continue
                
                # Initialize quiz session state
                st.session_state.pdf_quiz = {
                    'questions': [
                        {
                            'id': idx,
                            'question': q['question'],
                            'options': q['options'],
                            'correct_answer': q['correct_answer']
                        }
                        for idx, q in enumerate(quiz)
                    ],
                    'answers': {},
                    'submitted': False
                }
                
                st.success("Quiz generated successfully! Answer the questions below.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.text(traceback.format_exc())
    
    # Display and handle the PDF quiz if it exists
    if 'pdf_quiz' in st.session_state:
        st.subheader("PDF Generated Quiz")
        
        if not st.session_state.pdf_quiz['submitted']:
            # Display questions and collect answers
            for idx, q in enumerate(st.session_state.pdf_quiz['questions']):
                st.write(f"Q{idx+1}: {q['question']}")
                st.session_state.pdf_quiz['answers'][str(idx)] = st.radio(
                    f"Select your answer for Q{idx+1}",
                    q['options'],
                    key=f"pdf_q_{idx}",
                    index=None
                )
            
            if st.button("Submit Quiz"):
                st.session_state.pdf_quiz['submitted'] = True
                st.rerun()
        else:
            # Show results after submission
            st.subheader("Quiz Results")
            score = 0
            
            for idx, q in enumerate(st.session_state.pdf_quiz['questions']):
                user_answer = st.session_state.pdf_quiz['answers'].get(str(idx))
                correct_answer_text = q['correct_answer']  # This should be the full text
                
                # Get the index of the correct answer in options
                options = q['options']
                try:
                    correct_answer_index = options.index(correct_answer_text)
                    correct_answer_letter = chr(97 + correct_answer_index).upper()  # A, B, C, D
                except ValueError:
                    correct_answer_letter = "?"
                
                # Compare the actual selected text with correct text
                is_correct = user_answer == correct_answer_text
                
                if is_correct:
                    score += 1
                
                with st.expander(f"Question {idx+1}: {q['question']}", expanded=False):
                    st.markdown(f"Your answer: {user_answer if user_answer else 'Not answered'}")
                    st.markdown(f"Correct answer: {correct_answer_text} ({correct_answer_letter})")
                    if is_correct:
                        st.success("Correct!")
                    else:
                        st.error("Incorrect")
            
            st.success(f"### Your Score: {score}/{len(st.session_state.pdf_quiz['questions'])} 🎯")
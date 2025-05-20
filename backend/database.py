import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Returns a new database connection."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )

# Initialize the database connection
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

# Ensure database and table exist
def initialize_database():
    """Ensure the database and questions table exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subject VARCHAR(255) NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            difficulty VARCHAR(50) NOT NULL,
            question_type VARCHAR(50) NOT NULL,
            bloom_level VARCHAR(50) NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(50) NOT NULL,
            quiz_id VARCHAR(50) NOT NULL,
            score INT NOT NULL,
            total_questions INT NOT NULL,
            percentage FLOAT NOT NULL
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

# Insert a single question
def insert_question(subject, question, answer, difficulty, question_type, bloom_level):
    """Inserts a single question into the database with all required fields."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO questions (subject, question, answer, difficulty, question_type, bloom_level)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (subject, question, answer, difficulty, question_type, bloom_level)
    
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"✅ Inserted question: {question} with answer: {answer}")
    except Exception as e:
        print(f"❌ Error inserting question: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Bulk insert questions
def insert_bulk_questions(question_data):
    """ Insert multiple questions into the MySQL database efficiently. """
    if not question_data:
        print("⚠️ No questions to insert.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO questions (subject, question, answer, difficulty, question_type, bloom_level)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = [(q["subject"], q["question"], q["answer"], q["difficulty"], q["question_type"], q["bloom_level"]) for q in question_data]

    cursor.executemany(query, values)
    conn.commit()

    cursor.close()
    conn.close()
    print(f"✅ Inserted {len(question_data)} questions into the database.")

# Save quiz results
def save_quiz_result(user_id, quiz_id, score, total_questions):
    """ Stores quiz results in the database. """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO quiz_results (user_id, quiz_id, score, total_questions, percentage)
        VALUES (%s, %s, %s, %s, %s)
    """
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0.0
    values = (user_id, quiz_id, score, total_questions, percentage)
    
    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
    print(f"✅ Quiz result saved: User {user_id}, Score {score}/{total_questions}")

def get_options_for_question(question_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = "SELECT option_text FROM options_table WHERE question_id = %s"
    cursor.execute(query, (question_id,))
    
    options = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    connection.close()
    return options if options else ["Option 1", "Option 2", "Option 3", "Option 4"]

def get_questions(subject, question_type, difficulty, num_questions):
    """Fetch questions from database with proper parameters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT question, answer, difficulty, question_type 
            FROM questions 
            WHERE subject = %s AND question_type = %s AND difficulty = %s
            LIMIT %s
        """
        cursor.execute(query, (subject, question_type, difficulty, num_questions))
        questions = cursor.fetchall()
        
        return questions
        
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Ensure conn is available for import
all = ["conn", "cursor", "insert_bulk_questions", "insert_question", "get_questions", "save_quiz_result"]

# Initialize the database when the script is first executed
initialize_database()
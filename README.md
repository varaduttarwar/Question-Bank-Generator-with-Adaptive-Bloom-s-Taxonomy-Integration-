# 📚✨ AI-Powered Question Bank Generator with Adaptive Bloom’s Taxonomy Integration

Welcome to our intelligent academic tool built for COEP educators and students — a web-based AI-driven system that **automates question generation, quizzes, and PDF-based quiz creation**. It integrates **Bloom’s Taxonomy** to systematically assess various cognitive levels.

---

## 📑 Table of Contents
- [📝 Project Overview](#-project-overview)
- [🎯 Key Features](#-key-features)
- [🖥️ System Architecture](#-system-architecture)
- [⚙️ Tech Stack](#-tech-stack)
- [🚀 Core Functional Modes](#-core-functional-modes)
- [📊 Test Coverage](#-test-coverage)
- [🔮 Future Enhancements](#-future-enhancements)
- [📚 References](#-references)
- [📦 Run Locally](#-run-locally)
- [📑 .env Configuration](#-env-configuration)

---

## 📝 Project Overview

Traditional question paper creation is time-consuming, inconsistent, and lacks structured variation. This project introduces an **AI-Powered Question Bank Generator** that dynamically generates syllabus-aligned, Bloom’s Taxonomy-tagged questions, minimizing faculty workload while enhancing academic quality.

✔️ Automatically generate diverse questions  
✔️ Take interactive quizzes  
✔️ Generate quizzes from uploaded PDFs  

---

## 🎯 Key Features

✅ AI-driven question generation (MCQs, Short-Answer, True/False)  
✅ Bloom's Taxonomy level control  
✅ **3 Modes:**  
  - Generate Questions  
  - Take Quiz  
  - Upload PDF for quiz creation  
✅ Real-time scoring and feedback  
✅ Syllabus-adaptive question generation  
✅ Lightweight, interactive UI via Streamlit  

---

## 🖥️ System Architecture

A robust **3-tier architecture** ensuring scalability and maintainability:

- **Frontend:** Streamlit-based UI for educators and students  
- **Backend:** Python + LangChain + Groq’s Llama-3 LLM  
- **Database:** SQLite (or MySQL if configured) for storing questions and quiz results  

**UML diagrams, DFDs, ER diagrams, and activity diagrams** available in the project report.

---

## ⚙️ Tech Stack

| Component         | Technology                         |
|:-----------------|:----------------------------------|
| 💻 Frontend       | Streamlit                          |
| 🧠 AI/ML Backend  | LangChain + Groq’s Llama-3 (8b-8192)|
| 🗃️ Database       | SQLite / MySQL                      |
| 📖 Language       | Python 3.10+                        |

---

## 🚀 Core Functional Modes

### 📌 1️⃣ Generate Questions  
- Input subject, syllabus, number, type (MCQ/Short/True/False)  
- Auto-generates questions tagged with Bloom’s Taxonomy levels  

### 📌 2️⃣ Take Quiz  
- Choose topic, number of questions, type  
- Interactive quiz with real-time feedback and scoring  
- Auto-grade and display correct/incorrect answers  

### 📌 3️⃣ Upload PDF  
- Upload course syllabus or material (PDF)  
- Auto-extracts text and generates quiz questions  
- Supports multiple formats and Bloom’s levels  

---

## 📊 Test Coverage

✔️ Validated across **13+ rigorous test cases**:
- Question generation accuracy  
- PDF parsing robustness  
- Quiz submission and scoring  
- Database storage checks  
- UI responsiveness and error handling  

✅ All passed successfully. See full test case table in `G2-14.pdf`.

---

## 🔮 Future Enhancements

- COEP-specific fine-tuning with past papers  
- Image-based document parsing  
- Leaderboard and timed quiz features  
- Multi-language question generation  
- Learning Management System (LMS) integration

---

## 📚 References
- [Streamlit Docs](https://docs.streamlit.io/)
- [LangChain Docs](https://python.langchain.com/)
- [Groq API Docs](https://groq.com/)
- [IEEE SRS Standards](https://ieeexplore.ieee.org/document/1115056)
- [Bloom’s Taxonomy Reference (1956)](https://cft.vanderbilt.edu/guides-sub-pages/blooms-taxonomy/)

---

## 📦 Run Locally

**⚙️ Prerequisites:**
- Python 3.10+
- Virtual Environment (Recommended)
- `.env` file for API keys and DB credentials

### 🐍 Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


bash
git clone https://github.com/varaduttarwar/question-bank-generator.git
cd question-bank-generator
pip install -r requirements.txt
streamlit run -m /frontend/quiz_ui.py

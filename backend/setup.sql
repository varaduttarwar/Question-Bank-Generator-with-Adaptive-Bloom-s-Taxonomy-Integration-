-- 1️⃣ Create the Database (if it doesn't exist)
CREATE DATABASE IF NOT EXISTS exam_generator;

-- 2️⃣ Switch to the Database
USE exam_generator;

-- 3️⃣ Create a User and Grant Permissions (if not already created)
CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY '9765';
-- GRANT ALL PRIVILEGES ON exam_generator.* TO 'exam_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 4️⃣ Create the Questions Table
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    difficulty VARCHAR(50) NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    bloom_level VARCHAR(50) NOT NULL
);

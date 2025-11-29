-- Database setup script for AI Paragraph Titler
-- Run this script in MySQL to create the database and tables

CREATE DATABASE IF NOT EXISTS paragraph_titler_db;
USE paragraph_titler_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Saved Results Table
CREATE TABLE IF NOT EXISTS saved_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    paragraph TEXT NOT NULL,
    generated_title VARCHAR(500) NOT NULL,
    status VARCHAR(20),
    confidence VARCHAR(20),
    processing_time_ms FLOAT,
    character_count INT,
    word_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Show confirmation
SELECT 'Database and tables created successfully!' AS message;


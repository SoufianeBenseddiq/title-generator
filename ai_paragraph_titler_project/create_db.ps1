# PowerShell script to create MySQL database
# This script will prompt you for your MySQL password

Write-Host "Creating MySQL database..." -ForegroundColor Cyan
Write-Host ""

# Read MySQL password
$mysqlPassword = Read-Host "Enter your MySQL root password" -AsSecureString
$mysqlPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))

# Create database using MySQL command
$sqlCommands = @"
CREATE DATABASE IF NOT EXISTS paragraph_titler_db;
USE paragraph_titler_db;

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

SELECT 'Database and tables created successfully!' AS message;
"@

# Execute SQL
$sqlCommands | mysql -u root -p$mysqlPasswordPlain

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Database created successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Error creating database. Please check your MySQL password." -ForegroundColor Red
    Write-Host "You can also run the SQL manually:" -ForegroundColor Yellow
    Write-Host "  mysql -u root -p < setup_database.sql" -ForegroundColor Yellow
}


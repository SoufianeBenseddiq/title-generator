# Setup script for AI Paragraph Titler Backend
# Run this script in PowerShell from the ai_paragraph_titler_project directory

Write-Host "🚀 Setting up AI Paragraph Titler Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️  Virtual environment not found. Creating new one..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "📝 Checking for .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Red
    Write-Host "Creating .env file template..." -ForegroundColor Yellow
    
    $envContent = @"
# Security - CHANGE THIS to a random string!
SECRET_KEY=your-super-secret-key-change-this-to-random-string-123456789

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=paragraph_titler_db
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "✅ .env file created. Please edit it with your MySQL password!" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your MySQL password" -ForegroundColor White
Write-Host "2. Set up MySQL database (run setup_database.sql)" -ForegroundColor White
Write-Host "3. Run: python main.py" -ForegroundColor White
Write-Host ""


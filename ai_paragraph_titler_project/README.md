### 🚀 Run the Project Locally

Follow these steps to set up and run **AI Paragraph Titler** on your machine:

```bash
# AI Paragraph Titler API 🤖

An intelligent API that generates titles for paragraphs using AI, with user authentication and database storage.

---

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Git (optional)

---

## 🚀 Quick Start

### 1️⃣ Navigate to the project directory
```bash
cd ai_paragraph_titler_project
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
```

### 3️⃣ Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Set up MySQL Database

#### Option A: Using MySQL Command Line

```bash
mysql -u root -p
```

Then run the following SQL commands:

```sql
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
```

#### Option B: Using MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Open the SQL script file (if provided) or paste the SQL commands above
4. Execute the script

### 6️⃣ Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Windows (Command Prompt)
type nul > .env

# Windows (PowerShell)
New-Item .env

# macOS/Linux
touch .env
```

Edit the `.env` file and add the following:

```env
# Security
SECRET_KEY=your-super-secret-key-change-this-to-random-string-123456789

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=paragraph_titler_db
```

**⚠️ Important:**

- Change `SECRET_KEY` to a random, secure string
- Update `DB_PASSWORD` with your actual MySQL password
- Never commit the `.env` file to version control

### 7️⃣ Run the application

```bash
python main.py
```

The API will start running at: **http://localhost:8000**

---

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/

---

## 🔑 API Endpoints

### Authentication Endpoints

#### Register a New User

```http
POST /register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-15T10:30:00",
    "last_login": null
  }
}
```

#### Login

```http
POST /login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:** Same as registration response

#### Get Current User Info

```http
GET /me
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### Title Generation Endpoints

#### Generate Single Title

```http
POST /generate-title
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "paragraph": "Artificial intelligence is transforming the way we live and work. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions with remarkable accuracy.",
  "max_length": 15,
  "min_length": 5,
  "save_result": true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "result_id": 123,
    "title": "AI Transforming Life and Work",
    "paragraph": "Artificial intelligence is transforming...",
    "status": "optimal",
    "confidence": "high",
    "processing_time_ms": 245.67,
    "character_count": 156,
    "word_count": 28,
    "created_at": "2024-01-15T10:35:00"
  },
  "message": "Title generated successfully"
}
```

#### Generate Multiple Titles

```http
POST /generate-titles
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "paragraphs": [
    "First paragraph text here...",
    "Second paragraph text here...",
    "Third paragraph text here..."
  ],
  "max_length": 15,
  "min_length": 5,
  "save_results": true
}
```

---

### Saved Results Endpoints

#### Get Saved Results

```http
GET /saved-results?limit=20&offset=0
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Query Parameters:**

- `limit` (optional): Number of results to return (default: 50)
- `offset` (optional): Number of results to skip (default: 0)

#### Delete Saved Result

```http
DELETE /saved-results/{result_id}
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 🧪 Testing the API

### Using cURL

**Register:**

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

**Login:**

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

**Generate Title (replace TOKEN with your access token):**

```bash
curl -X POST http://localhost:8000/generate-title \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d "{\"paragraph\":\"Your paragraph text here\"}"
```

### Using Python Requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Register
response = requests.post(f"{BASE_URL}/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})
data = response.json()
token = data["access_token"]

# 2. Generate Title
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/generate-title",
    headers=headers,
    json={"paragraph": "Your paragraph text here"}
)
print(response.json())

# 3. Get Saved Results
response = requests.get(f"{BASE_URL}/saved-results", headers=headers)
print(response.json())
```

---

## 🛠️ Troubleshooting

### Database Connection Issues

```bash
# Check if MySQL is running
# Windows:
net start MySQL80

# macOS:
brew services start mysql

# Linux:
sudo systemctl start mysql
```

### Port Already in Use

If port 8000 is already in use, modify `main.py`:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)  # Change port
```

### Model Loading Issues

Ensure the AI model is in the correct directory:

```
ai_paragraph_titler_project/
├── ai_paragraph_titler_model/
│   ├── config.json
│   ├── pytorch_model.bin
│   └── ... (other model files)
├── main.py
└── .env
```

### Environment Variables Not Loading

Make sure `python-dotenv` is installed and `.env` file is in the root directory.

---

## 📁 Project Structure

```
ai_paragraph_titler_project/
├── main.py                          # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (create this)
├── .gitignore                      # Git ignore file
├── README.md                       # This file
├── ai_paragraph_titler_model/      # AI model directory
│   └── (model files)
└── venv/                           # Virtual environment (created by you)
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong SECRET_KEY** - generate a random string
3. **Use HTTPS in production** - not HTTP
4. **Change default passwords** for MySQL
5. **Set strong password requirements** for users
6. **Implement rate limiting** for production
7. **Regular database backups**

---

## 🚢 Production Deployment

For production deployment, consider:

1. **Use a production WSGI server:**

   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
2. **Set up HTTPS** with SSL certificates
3. **Use environment-specific `.env` files**
4. **Enable CORS only for your frontend domain**
5. **Set up proper logging and monitoring**
6. **Use a production database** (not localhost)

---

## 📝 License

[Your License Here]

---

## 👥 Contributors

[Your Name/Team]

---

## 📧 Support

For issues or questions, please contact: [your-email@example.com]

---

**Happy Coding! 🎉**

```

```

# 📁 Codebase Architecture & Logic Explanation

## Overview

This document provides a comprehensive explanation of the codebase structure, file organization, and the logic behind each component of the AI Paragraph Titler project.

---

## 🗂️ Project Structure

```
ai_paragraph_titler_project/
├── main.py                          # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (not in repo)
├── setup_database.sql              # Database schema
├── ai_paragraph_titler_model/      # Fine-tuned BART model
│   ├── config.json                 # Model configuration
│   ├── model.safetensors          # Model weights
│   ├── tokenizer_config.json      # Tokenizer settings
│   └── ...
├── ai_paragraph_titler_trainer.ipynb  # Model training notebook
├── data/                           # Training data
│   ├── trainig_dataset.csv         # Training dataset
│   └── sample_text.txt            # Sample text
└── results/                        # Training results
    └── output.txt
```

---

## 📄 Core Files Explained

### 1. `main.py` - FastAPI Backend Application

**Purpose**: Main application file containing all API endpoints, business logic, and model integration.

#### File Structure

```python
# Imports & Configuration (Lines 1-45)
├── FastAPI, CORS, Security imports
├── Transformers pipeline for model
├── Database connection (MySQL)
├── Authentication (JWT, bcrypt)
└── Environment variables loading

# Lifespan Management (Lines 44-68)
├── Model loading on startup
├── Database pool creation
└── Cleanup on shutdown

# Database Functions (Lines 85-93)
├── get_db_connection() - Get connection from pool

# Authentication Functions (Lines 96-155)
├── hash_password() - Hash passwords with bcrypt
├── verify_password() - Verify password against hash
├── create_access_token() - Generate JWT tokens
├── decode_token() - Validate and decode JWT
└── get_current_user() - Get authenticated user

# Pydantic Models (Lines 158-233)
├── UserRegister, UserLogin, UserResponse
├── ParagraphRequest, MultipleParagraphsRequest
├── TitleResult, TitleResponse
└── SavedResultsResponse

# Helper Functions (Lines 236-324)
├── evaluate_title_status() - Assess title quality
├── generate_title() - Core title generation logic
└── save_result_to_db() - Persist results

# API Endpoints (Lines 327-607)
├── GET / - Health check
├── POST /register - User registration
├── POST /login - User authentication
├── GET /me - Get current user
├── POST /generate-title - Generate single title
├── POST /generate-titles - Generate multiple titles
├── GET /saved-results - Get user's history
├── DELETE /saved-results/{id} - Delete result
└── GET /health - Detailed health check
```

#### Key Logic Sections

##### A. Model Loading (Lines 48-59)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and database on startup"""
    global summarizer, db_pool
    
    # Load AI model
    summarizer = pipeline(
        "summarization", 
        model="./ai_paragraph_titler_model"
    )
    
    # Create database connection pool
    db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
```

**Logic**: 
- Uses FastAPI's lifespan context manager
- Loads model once at startup (not per request) for efficiency
- Creates database connection pool for better performance
- Global variables ensure model is accessible to all endpoints

##### B. Title Generation (Lines 268-300)
```python
def generate_title(paragraph: str, max_length: int, min_length: int) -> dict:
    """Generate title for a single paragraph"""
    start_time = time.time()
    
    # Validate input
    if not paragraph or len(paragraph.strip()) == 0:
        raise ValueError("Paragraph cannot be empty")
    
    # Generate title using model
    result = summarizer(
        paragraph,
        max_length=max_length,
        min_length=min_length,
        do_sample=False  # Deterministic output
    )[0]
    title = result['summary_text']
    
    # Calculate metrics
    processing_time = (time.time() - start_time) * 1000
    char_count = len(paragraph)
    word_count = len(paragraph.split())
    status, confidence = evaluate_title_status(title, paragraph)
    
    return {
        "title": title,
        "paragraph": paragraph,
        "status": status,
        "confidence": confidence,
        "processing_time_ms": round(processing_time, 2),
        "character_count": char_count,
        "word_count": word_count
    }
```

**Logic Flow**:
1. **Input Validation**: Ensures paragraph is not empty
2. **Model Inference**: Calls the BART model via Hugging Face pipeline
3. **Metrics Calculation**: 
   - Processing time (performance metric)
   - Character/word counts (input analysis)
   - Status and confidence (quality assessment)
4. **Return Structured Data**: All information in a dictionary

##### C. Title Quality Evaluation (Lines 238-265)
```python
def evaluate_title_status(title: str, paragraph: str) -> tuple[str, str]:
    """Evaluate the quality/status of generated title"""
    title_words = len(title.split())
    paragraph_words = len(paragraph.split())
    
    # Determine status based on title length
    if title_words < 3:
        return "short", "medium"
    elif title_words >= 3 and title_words <= 8:
        status = "optimal"
    else:
        status = "verbose"
    
    # Determine confidence based on paragraph length
    if paragraph_words < 10:
        confidence = "low"
    elif paragraph_words < 50:
        confidence = "medium"
    else:
        confidence = "high"
    
    # Check for truncation
    if title.endswith(('...', '..', '..')):
        status = "truncated"
        confidence = "medium"
    
    return status, confidence
```

**Logic**:
- **Status**: Categorizes title length (short/optimal/verbose/truncated)
- **Confidence**: Assesses reliability based on input paragraph length
- **Heuristics**: Simple but effective rules for quality assessment

##### D. Authentication Flow (Lines 96-155)
```python
def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    # Fetch user from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, username, email, first_name, last_name, is_active 
         FROM users WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    
    if not user or not user['is_active']:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user
```

**Authentication Logic**:
1. **Token Creation**: JWT with user_id and expiration
2. **Token Validation**: Decode and verify signature
3. **User Verification**: Check user exists and is active
4. **Dependency Injection**: FastAPI's `Depends()` automatically extracts token from request

##### E. Database Operations (Lines 299-324)
```python
def save_result_to_db(user_id: int, result_data: dict) -> int:
    """Save a title result to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO saved_results 
        (user_id, paragraph, generated_title, status, confidence, 
         processing_time_ms, character_count, word_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        result_data['paragraph'],
        result_data['title'],
        result_data['status'],
        result_data['confidence'],
        result_data['processing_time_ms'],
        result_data['character_count'],
        result_data['word_count']
    ))
    conn.commit()
    return cursor.lastrowid
```

**Database Logic**:
- **Connection Pooling**: Reuses connections for efficiency
- **Transaction Management**: Commits after successful insert
- **Error Handling**: Proper cleanup in finally blocks
- **Return ID**: Returns the inserted record ID for reference

---

### 2. `setup_database.sql` - Database Schema

**Purpose**: SQL script to create the database and tables.

#### Schema Structure

```sql
-- Database Creation
CREATE DATABASE IF NOT EXISTS paragraph_titler_db;

-- Users Table
CREATE TABLE users (
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
CREATE TABLE saved_results (
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

**Design Decisions**:
- **Foreign Key**: Ensures data integrity (cascade delete)
- **Indexes**: Optimize queries on user_id and created_at
- **Timestamps**: Track creation and last login times
- **Boolean Flags**: `is_active` for soft deletion

---

### 3. `ai_paragraph_titler_trainer.ipynb` - Model Training

**Purpose**: Jupyter notebook for fine-tuning the BART model on paragraph-title pairs.

#### Training Pipeline

```python
# 1. Load Dataset
df = pd.read_csv('trainig_dataset.csv')  # 2,225 examples
dataset = Dataset.from_pandas(df)

# 2. Load Pre-trained Model
model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")

# 3. Preprocess Data
def preprocess(examples):
    inputs = tokenizer(examples["paragraph"], max_length=512, truncation=True)
    labels = tokenizer(examples["title"], max_length=64, truncation=True)
    inputs["labels"] = labels["input_ids"]
    return inputs

tokenized_dataset = dataset.map(preprocess, batched=True)

# 4. Configure Training
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    warmup_steps=100,
    weight_decay=0.01,
)

# 5. Train Model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)
trainer.train()

# 6. Save Model
model.save_pretrained("./ai_paragraph_titler_model")
tokenizer.save_pretrained("./ai_paragraph_titler_model")
```

**Training Logic**:
1. **Data Preparation**: CSV → Hugging Face Dataset
2. **Tokenization**: Convert text to model-readable format
3. **Fine-Tuning**: Update model weights on title generation task
4. **Model Persistence**: Save for inference use

---

### 4. `ai_paragraph_titler_model/config.json` - Model Configuration

**Purpose**: Defines the BART model architecture and parameters.

#### Key Configuration Values

```json
{
  "model_type": "bart",
  "architectures": ["BartForConditionalGeneration"],
  "encoder_layers": 6,
  "decoder_layers": 6,
  "d_model": 768,
  "encoder_attention_heads": 12,
  "decoder_attention_heads": 12,
  "vocab_size": 50265,
  "max_position_embeddings": 1024
}
```

**Meaning**:
- **6 Layers**: Both encoder and decoder have 6 transformer layers
- **768 Dimensions**: Hidden state size (model capacity)
- **12 Attention Heads**: Multi-head attention for better context understanding
- **50,265 Vocabulary**: Number of unique tokens the model knows

---

## 🔄 Data Flow

### Request Flow: Generate Title

```
1. Frontend Request
   POST /generate-title
   {
     "paragraph": "AI is transforming...",
     "max_length": 15,
     "min_length": 5
   }
   ↓
2. Authentication Middleware
   - Extract JWT token from Authorization header
   - Validate token and get user
   ↓
3. API Endpoint Handler
   @app.post("/generate-title")
   - Validate request body
   - Call generate_title() function
   ↓
4. Title Generation Function
   generate_title(paragraph, max_length, min_length)
   - Validate input
   - Call model: summarizer(paragraph, ...)
   - Evaluate quality
   - Calculate metrics
   ↓
5. Database Save (if requested)
   save_result_to_db(user_id, result_data)
   - Insert into saved_results table
   ↓
6. Response
   {
     "success": true,
     "data": {
       "title": "AI transforms healthcare",
       "status": "optimal",
       "confidence": "high",
       ...
     }
   }
```

---

## 🔐 Security Architecture

### Authentication Flow

```
1. Registration
   User → POST /register → Hash Password (bcrypt) → Save to DB → Return JWT
   
2. Login
   User → POST /login → Verify Password → Return JWT
   
3. Authenticated Request
   Request → Extract JWT → Validate Token → Get User from DB → Process Request
```

### Security Measures

1. **Password Hashing**: bcrypt with salt (one-way encryption)
2. **JWT Tokens**: Signed tokens with expiration (24 hours)
3. **SQL Injection Prevention**: Parameterized queries
4. **CORS**: Restricted to frontend origins only
5. **Input Validation**: Pydantic models validate all inputs

---

## 🗄️ Database Design

### Entity Relationship

```
users (1) ────< (many) saved_results
```

**Relationships**:
- One user can have many saved results
- Cascade delete: Deleting user deletes all their results

### Query Patterns

```sql
-- Get user's saved results (paginated)
SELECT * FROM saved_results 
WHERE user_id = ? 
ORDER BY created_at DESC 
LIMIT ? OFFSET ?

-- Get user by username
SELECT * FROM users 
WHERE username = ? AND is_active = TRUE

-- Insert new result
INSERT INTO saved_results (...) 
VALUES (...)
```

---

## 🧪 Error Handling

### Error Types & Handling

```python
# 1. Validation Errors (400)
if not paragraph or len(paragraph.strip()) == 0:
    raise ValueError("Paragraph cannot be empty")
→ Returns: HTTP 400 Bad Request

# 2. Authentication Errors (401)
if not user or not user['is_active']:
    raise HTTPException(status_code=401, detail="User not found")
→ Returns: HTTP 401 Unauthorized

# 3. Model Errors (503)
if summarizer is None:
    raise HTTPException(status_code=503, detail="Model not loaded yet")
→ Returns: HTTP 503 Service Unavailable

# 4. Database Errors (500)
try:
    # Database operation
except mysql.connector.Error as e:
    logger.error(f"Database error: {str(e)}")
    raise HTTPException(status_code=500, detail="Database error")
→ Returns: HTTP 500 Internal Server Error
```

---

## 📊 Performance Optimizations

### 1. Model Loading
- **Lazy Loading**: Model loaded once at startup (not per request)
- **Global Variable**: Shared across all requests

### 2. Database Connection Pooling
```python
db_pool = MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5  # Reuse 5 connections
)
```
- **Reuse Connections**: Avoids connection overhead
- **Limited Pool Size**: Prevents resource exhaustion

### 3. Async Operations
- **FastAPI Async**: Non-blocking request handling
- **Database Operations**: Can be made async (future improvement)

---

## 🔧 Configuration Management

### Environment Variables (.env)

```env
SECRET_KEY=your-secret-key          # JWT signing key
DB_HOST=localhost                   # Database host
DB_USER=root                        # Database user
DB_PASSWORD=your_password           # Database password
DB_NAME=paragraph_titler_db         # Database name
```

### Configuration Loading

```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file

SECRET_KEY = os.getenv("SECRET_KEY", "default")
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    ...
}
```

**Benefits**:
- **Security**: Secrets not in code
- **Flexibility**: Easy environment-specific configs
- **Default Values**: Fallback for missing variables

---

## 🚀 API Endpoints Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/` | GET | No | Health check |
| `/register` | POST | No | User registration |
| `/login` | POST | No | User authentication |
| `/me` | GET | Yes | Get current user |
| `/generate-title` | POST | Yes | Generate single title |
| `/generate-titles` | POST | Yes | Generate multiple titles |
| `/saved-results` | GET | Yes | Get user's history |
| `/saved-results/{id}` | DELETE | Yes | Delete a result |
| `/health` | GET | No | Detailed health check |

---

## 📝 Code Quality & Best Practices

### 1. Type Hints
```python
def generate_title(paragraph: str, max_length: int, min_length: int) -> dict:
```
- Improves code readability
- Enables IDE autocomplete
- Catches type errors early

### 2. Docstrings
```python
def generate_title(paragraph: str, max_length: int, min_length: int) -> dict:
    """Generate title for a single paragraph"""
```
- Documents function purpose
- Helps with code maintenance

### 3. Error Logging
```python
logger.error(f"Error generating title: {str(e)}")
```
- Centralized logging
- Helps with debugging
- Production monitoring

### 4. Pydantic Models
```python
class ParagraphRequest(BaseModel):
    paragraph: str = Field(..., min_length=1)
    max_length: Optional[int] = Field(15, ge=5, le=50)
```
- Automatic validation
- Type checking
- API documentation

---

## 🔄 Future Improvements

### Potential Enhancements

1. **Caching**: Cache model results for identical paragraphs
2. **Rate Limiting**: Prevent abuse
3. **Async Database**: Use async MySQL driver
4. **Background Tasks**: Process multiple titles in background
5. **Model Versioning**: Support multiple model versions
6. **Analytics**: Track usage patterns
7. **Batch Processing**: Optimize multiple title generation

---

## 📚 Dependencies Explained

### Core Dependencies

- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **transformers**: Hugging Face library for AI models
- **torch**: PyTorch for model inference
- **mysql-connector-python**: MySQL database driver
- **bcrypt**: Password hashing
- **PyJWT**: JWT token handling
- **pydantic**: Data validation
- **python-dotenv**: Environment variable management

---

**Last Updated**: 2024
**Version**: 2.0.0


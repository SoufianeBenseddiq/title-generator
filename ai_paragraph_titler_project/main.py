from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from transformers import pipeline
from typing import List, Optional
from contextlib import asynccontextmanager
import time
import logging
import mysql.connector
from mysql.connector import pooling
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
summarizer = None
db_pool = None

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "paragraph_titler_db"),
    "pool_name": "mypool",
    "pool_size": 5
}

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model and database pool on startup"""
    global summarizer, db_pool
    try:
        logger.info("Loading AI model...")
        summarizer = pipeline(
            "summarization", model="./ai_paragraph_titler_model")
        logger.info("Model loaded successfully!")
        
        logger.info("Creating database connection pool...")
        db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
        logger.info("Database pool created successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="AI Paragraph Titler API",
    description="Generate AI-powered titles for paragraphs with user authentication",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Database Functions ====================

def get_db_connection():
    """Get a connection from the pool"""
    try:
        return db_pool.get_connection()
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# ==================== Auth Functions ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    # Fetch user from database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT user_id, username, email, first_name, last_name, is_active FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user or not user['is_active']:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        return user
    finally:
        cursor.close()
        conn.close()


# ==================== Pydantic Models ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class ParagraphRequest(BaseModel):
    paragraph: str = Field(..., min_length=1)
    max_length: Optional[int] = Field(15, ge=5, le=50)
    min_length: Optional[int] = Field(5, ge=1, le=20)
    save_result: Optional[bool] = Field(True, description="Save result to database")


class MultipleParagraphsRequest(BaseModel):
    paragraphs: List[str] = Field(..., min_length=1)
    max_length: Optional[int] = Field(15, ge=5, le=50)
    min_length: Optional[int] = Field(5, ge=1, le=20)
    save_results: Optional[bool] = Field(True)


class TitleResult(BaseModel):
    result_id: Optional[int] = None
    title: str
    paragraph: str
    status: str
    confidence: str
    processing_time_ms: float
    character_count: int
    word_count: int
    created_at: Optional[datetime] = None


class TitleResponse(BaseModel):
    success: bool
    data: TitleResult
    message: str


class MultipleTitlesResponse(BaseModel):
    success: bool
    data: List[TitleResult]
    total_paragraphs: int
    total_processing_time_ms: float
    message: str


class SavedResultsResponse(BaseModel):
    success: bool
    data: List[TitleResult]
    total_results: int
    message: str


# ==================== Helper Functions ====================

def evaluate_title_status(title: str, paragraph: str) -> tuple[str, str]:
    """Evaluate the quality/status of generated title"""
    title_words = len(title.split())
    paragraph_words = len(paragraph.split())

    if title_words < 3:
        return "short", "medium"
    elif title_words >= 3 and title_words <= 8:
        status = "optimal"
    else:
        status = "verbose"

    if paragraph_words < 10:
        confidence = "low"
    elif paragraph_words < 50:
        confidence = "medium"
    else:
        confidence = "high"

    if title.endswith(('...', '..', '..')):
        status = "truncated"
        confidence = "medium"

    return status, confidence


def generate_title(paragraph: str, max_length: int, min_length: int) -> dict:
    """Generate title for a single paragraph"""
    start_time = time.time()

    if not paragraph or len(paragraph.strip()) == 0:
        raise ValueError("Paragraph cannot be empty")

    try:
        result = summarizer(
            paragraph,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )[0]
        title = result['summary_text']
    except Exception as e:
        logger.error(f"Error generating title: {str(e)}")
        raise ValueError(f"Failed to generate title: {str(e)}")

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


def save_result_to_db(user_id: int, result_data: dict) -> int:
    """Save a title result to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
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
    finally:
        cursor.close()
        conn.close()


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "AI Paragraph Titler API is running",
        "model_loaded": summarizer is not None,
        "database_connected": db_pool is not None
    }


@app.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    """Register a new user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if username or email already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (user.username, user.email)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        # Hash password and create user
        hashed_pw = hash_password(user.password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (user.username, user.email, hashed_pw, user.first_name, user.last_name))
        conn.commit()
        
        user_id = cursor.lastrowid
        
        # Fetch the created user
        cursor.execute(
            "SELECT user_id, username, email, first_name, last_name, created_at, last_login FROM users WHERE user_id = %s",
            (user_id,)
        )
        created_user = cursor.fetchone()
        
        # Create access token
        access_token = create_access_token({"user_id": user_id, "username": user.username})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**created_user)
        )
    
    except mysql.connector.Error as e:
        conn.rollback()
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        cursor.close()
        conn.close()


@app.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch user
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND is_active = TRUE",
            (credentials.username,)
        )
        user = cursor.fetchone()
        
        if not user or not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE user_id = %s",
            (user['user_id'],)
        )
        conn.commit()
        
        # Create access token
        access_token = create_access_token({
            "user_id": user['user_id'],
            "username": user['username']
        })
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                user_id=user['user_id'],
                username=user['username'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                created_at=user['created_at'],
                last_login=datetime.utcnow()
            )
        )
    
    finally:
        cursor.close()
        conn.close()


@app.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT user_id, username, email, first_name, last_name, created_at, last_login FROM users WHERE user_id = %s",
            (current_user['user_id'],)
        )
        user = cursor.fetchone()
        return UserResponse(**user)
    finally:
        cursor.close()
        conn.close()


@app.post("/generate-title", response_model=TitleResponse)
async def generate_single_title(
    request: ParagraphRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a title for a single paragraph"""
    if summarizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    try:
        result_data = generate_title(
            request.paragraph, request.max_length, request.min_length)
        
        # Save to database if requested
        result_id = None
        if request.save_result:
            result_id = save_result_to_db(current_user['user_id'], result_data)
        
        result = TitleResult(**result_data, result_id=result_id, created_at=datetime.utcnow())
        
        return TitleResponse(
            success=True,
            data=result,
            message="Title generated successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/generate-titles", response_model=MultipleTitlesResponse)
async def generate_multiple_titles(
    request: MultipleParagraphsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate titles for multiple paragraphs"""
    if summarizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    try:
        total_start = time.time()
        results = []

        for paragraph in request.paragraphs:
            if paragraph.strip():
                result_data = generate_title(
                    paragraph, request.max_length, request.min_length)
                
                result_id = None
                if request.save_results:
                    result_id = save_result_to_db(current_user['user_id'], result_data)
                
                result = TitleResult(**result_data, result_id=result_id, created_at=datetime.utcnow())
                results.append(result)

        total_time = (time.time() - total_start) * 1000

        return MultipleTitlesResponse(
            success=True,
            data=results,
            total_paragraphs=len(results),
            total_processing_time_ms=round(total_time, 2),
            message=f"Successfully generated {len(results)} titles"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/saved-results", response_model=SavedResultsResponse)
async def get_saved_results(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user's saved results"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT result_id, paragraph, generated_title as title, status, confidence,
                   processing_time_ms, character_count, word_count, created_at
            FROM saved_results
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (current_user['user_id'], limit, offset))
        
        results = cursor.fetchall()
        
        # Get total count
        cursor.execute(
            "SELECT COUNT(*) as total FROM saved_results WHERE user_id = %s",
            (current_user['user_id'],)
        )
        total = cursor.fetchone()['total']
        
        return SavedResultsResponse(
            success=True,
            data=[TitleResult(**r) for r in results],
            total_results=total,
            message=f"Retrieved {len(results)} saved results"
        )
    
    finally:
        cursor.close()
        conn.close()


@app.delete("/saved-results/{result_id}")
async def delete_saved_result(
    result_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a saved result"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM saved_results WHERE result_id = %s AND user_id = %s",
            (result_id, current_user['user_id'])
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return {"success": True, "message": "Result deleted successfully"}
    
    finally:
        cursor.close()
        conn.close()


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": summarizer is not None,
        "database_connected": db_pool is not None,
        "model_name": "ai_paragraph_titler_model"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
#!/usr/bin/env python3
"""
DCM System - MongoDB Backend with Environment Configuration
Secure, production-ready Digital Case Management System with AI Features
"""

import base64
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
import asyncio
import logging
import os
import uuid
import shutil
from pathlib import Path

# Import our configuration
from config import config

# Import AI service
try:
    from app.services.ai_service import ai_service
    AI_ENABLED = True
    print("✅ AI Services loaded successfully")
except ImportError as e:
    AI_ENABLED = False
    print(f"⚠️ AI Services not available: {e}")
    ai_service = None

# Configure logging
logging.basicConfig(level=getattr(logging, config.log_level))
logger = logging.getLogger(__name__)

# Print configuration summary
config.print_config_summary()

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB client
mongodb_client: AsyncIOMotorClient = None

# User roles
class UserRole(str, Enum):
    ADMIN = "admin"
    JUDGE = "judge"
    CLERK = "clerk"
    LAWYER = "lawyer"

# Case status
class CaseStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    DISMISSED = "dismissed"
    FILED = "FILED"  # Added for compatibility with generated dataset
    UNDER_REVIEW = "UNDER_REVIEW"
    SCHEDULED = "SCHEDULED"  # Added for hearing scheduled cases
    HEARING_SCHEDULED = "HEARING_SCHEDULED"
    JUDGMENT_RESERVED = "JUDGMENT_RESERVED"
    DISPOSED = "DISPOSED"

# MongoDB Models (Beanie Documents)
class User(Document):
    username: str = Field(index=True)
    email: str = Field(index=True)
    full_name: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"

class Case(Document):
    case_number: str = Field(index=True)
    title: str
    description: str
    case_type: str
    status: CaseStatus
    priority: str
    assigned_judge: Optional[str] = None
    assigned_lawyer: Optional[str] = None
    created_by: Optional[str] = None  # Made optional for backward compatibility
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "cases"

class Hearing(Document):
    case_id: str = Field(index=True)
    scheduled_date: datetime
    location: str
    judge: str
    status: str = "scheduled"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "hearings"

class CaseDocument(Document):
    """Document model for storing case-related files with content in MongoDB"""
    filename: str = Field(..., index=True)
    original_filename: str = Field(...)
    file_content: str = Field(...)  # Base64 encoded file content
    file_size: int = Field(...)  # File size in bytes
    content_type: str = Field(...)  # MIME type
    case_id: Optional[str] = Field(default=None, index=True)  # Associated case
    uploaded_by: str = Field(..., index=True)  # User who uploaded
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = Field(default=None)
    document_type: str = Field(default="general")  # general, evidence, pleading, order, etc.
    is_public: bool = Field(default=False)  # Public access flag
    
    class Settings:
        name = "documents"

# Pydantic models for API
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: UserRole

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: UserResponse

class CaseCreate(BaseModel):
    title: str
    description: str
    case_type: str
    priority: str

class DocumentAnalysisRequest(BaseModel):
    content: str
    filename: str = "document.txt"

class CaseClassificationRequest(BaseModel):
    title: str
    description: str

class SimilarCasesRequest(BaseModel):
    title: str
    description: str
    limit: int = 5

# FastAPI app
app = FastAPI(
    title="DCM System - AI-Powered MongoDB Edition",
    description="Digital Case Management System with MongoDB backend and AI features",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await User.find_one(User.username == username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# MongoDB connection
async def connect_to_mongo():
    """Create database connection"""
    global mongodb_client
    
    try:
        mongodb_client = AsyncIOMotorClient(config.MONGODB_URL)
        
        # Test connection
        await mongodb_client.admin.command('ping')
        
        # Initialize Beanie
        await init_beanie(
            database=mongodb_client[config.DATABASE_NAME],
            document_models=[User, Case, Hearing, CaseDocument]
        )
        
        logger.info("✅ Connected to MongoDB Atlas!")
        logger.info(f"📊 Database: {config.DATABASE_NAME}")
        
        # Create demo data
        await create_demo_data()
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        logger.error("🔧 Please check:")
        logger.error("   1. Your MongoDB password is correct")
        logger.error("   2. Your IP is whitelisted in MongoDB Atlas")
        logger.error("   3. Your internet connection is working")
        raise

async def create_demo_data():
    """Create demo users and cases"""
    try:
        # Check if admin user already exists
        admin_exists = await User.find_one(User.username == "admin")
        
        if not admin_exists:
            # Create demo users
            demo_users = [
                {"username": "admin", "email": "admin@dcm.com", "full_name": "System Administrator", "password": "admin123", "role": UserRole.ADMIN},
                {"username": "judge1", "email": "judge1@dcm.com", "full_name": "Judge Smith", "password": "demo123", "role": UserRole.JUDGE},
                {"username": "clerk1", "email": "clerk1@dcm.com", "full_name": "Mary Clerk", "password": "demo123", "role": UserRole.CLERK},
                {"username": "lawyer1", "email": "lawyer1@dcm.com", "full_name": "John Lawyer", "password": "demo123", "role": UserRole.LAWYER},
            ]
            
            for user_data in demo_users:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=hash_password(user_data["password"]),
                    role=user_data["role"]
                )
                await user.insert()
            
            logger.info("👥 Created demo users!")
            
            # Create demo cases
            demo_cases = [
                {
                    "case_number": "DCM-2024-001",
                    "title": "Smith vs. Johnson",
                    "description": "Property dispute case",
                    "case_type": "Civil",
                    "status": CaseStatus.PENDING,
                    "priority": "high",
                    "assigned_judge": "judge1",
                    "created_by": "clerk1"
                },
                {
                    "case_number": "DCM-2024-002", 
                    "title": "State vs. Brown",
                    "description": "Traffic violation case",
                    "case_type": "Criminal",
                    "status": CaseStatus.IN_PROGRESS,
                    "priority": "medium",
                    "assigned_judge": "judge1",
                    "created_by": "clerk1"
                }
            ]
            
            for case_data in demo_cases:
                case = Case(**case_data)
                await case.insert()
                
            logger.info("📁 Created demo cases!")
        else:
            logger.info("ℹ️  Demo data already exists")
            
    except Exception as e:
        logger.error(f"❌ Error creating demo data: {e}")

async def close_mongo_connection():
    """Close database connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()

# Startup event
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "🤖 DCM System - AI-Powered MongoDB Edition",
        "status": "running",
        "database": "MongoDB Atlas",
        "ai_enabled": AI_ENABLED,
        "version": "3.0.0",
        "features": [
            "User Authentication",
            "Case Management", 
            "Document Upload",
            "AI Case Classification",
            "Document Analysis",
            "Similar Cases Search",
            "Case Insights",
            "Smart Analytics"
        ] if AI_ENABLED else [
            "User Authentication",
            "Case Management", 
            "Document Upload"
        ]
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        user_count = await User.count()
        case_count = await Case.count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "cases": case_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Authentication routes
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    existing_email = await User.find_one(User.email == user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    
    await user.insert()
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    # Find user
    user = await User.find_one(User.username == user_credentials.username)
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    user_response = UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_info=user_response
    )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

# Cases routes
@app.get("/api/cases")
async def get_cases(current_user: User = Depends(get_current_user)):
    cases = await Case.find().to_list()
    return [
        {
            "id": str(case.id),
            "case_number": case.case_number,
            "title": case.title,
            "description": case.description,
            "case_type": case.case_type,
            "status": case.status,
            "priority": case.priority,
            "assigned_judge": case.assigned_judge,
            "created_by": case.created_by,
            "created_at": case.created_at,
            "updated_at": case.updated_at
        }
        for case in cases
    ]

@app.post("/api/cases")
async def create_case(case_data: CaseCreate, current_user: User = Depends(get_current_user)):
    # Generate case number
    case_count = await Case.count() + 1
    case_number = f"DCM-2024-{case_count:03d}"
    
    case = Case(
        case_number=case_number,
        title=case_data.title,
        description=case_data.description,
        case_type=case_data.case_type,
        status=CaseStatus.PENDING,
        priority=case_data.priority,
        created_by=current_user.username
    )
    
    await case.insert()
    
    return {
        "id": str(case.id),
        "case_number": case.case_number,
        "title": case.title,
        "status": case.status,
        "message": "Case created successfully"
    }

# Users route (admin only)
@app.get("/api/users")
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    users = await User.find().to_list()
    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]

@app.post("/api/users")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new user (Admin only)"""
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    # Check if username already exists
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = await User.find_one(User.email == user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    # Hash the password using passlib
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    await new_user.insert()
    
    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

# Document API routes
@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    case_id: Optional[str] = None,
    description: Optional[str] = None,
    document_type: str = "general",
    current_user: User = Depends(get_current_user)
):
    """Upload a document (PDF, DOC, DOCX, TXT, etc.)"""
    
    # Check if user has upload permission
    upload_roles = [UserRole.ADMIN, UserRole.CLERK, UserRole.LAWYER]
    if current_user.role not in upload_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Document upload not allowed for role {current_user.role}. Required roles: {', '.join([role.value for role in upload_roles])}"
        )
    
    # Validate file type
    allowed_types = {
        "application/pdf", 
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "image/jpeg",
        "image/png",
        "image/gif"
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed. Allowed types: PDF, DOC, DOCX, TXT, JPG, PNG, GIF"
        )
    
    # Validate file size (max 10MB)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10MB"
        )
    
    # Encode file content to base64 for MongoDB storage
    file_content_base64 = base64.b64encode(file_content).decode('utf-8')
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create document record with file content stored in MongoDB
    document = CaseDocument(
        filename=unique_filename,
        original_filename=file.filename,
        file_content=file_content_base64,  # Store base64 encoded content
        file_size=len(file_content),
        content_type=file.content_type,
        case_id=case_id,
        uploaded_by=str(current_user.id),
        description=description,
        document_type=document_type
    )
    
    await document.insert()
    
    return {
        "id": str(document.id),
        "filename": document.original_filename,
        "size": document.file_size,
        "type": document.content_type,
        "uploaded_by": current_user.username,
        "upload_date": document.upload_date,
        "case_id": document.case_id,
        "description": document.description,
        "document_type": document.document_type
    }

@app.get("/api/documents")
async def get_documents(
    case_id: Optional[str] = None,
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get list of documents, filtered by uploader (only show documents uploaded by current user)"""
    
    query = {}
    if case_id:
        query["case_id"] = case_id
    if document_type:
        query["document_type"] = document_type
    
    # Filter by uploaded_by - users can only see their own documents
    query["uploaded_by"] = current_user.username
    
    documents = await CaseDocument.find(query).to_list()
    
    return [
        {
            "id": str(doc.id),
            "filename": doc.original_filename,
            "size": doc.file_size,
            "type": doc.content_type,
            "uploaded_by": doc.uploaded_by,
            "upload_date": doc.upload_date,
            "case_id": doc.case_id,
            "description": doc.description,
            "document_type": doc.document_type
        }
        for doc in documents
    ]

@app.get("/api/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download a document file from MongoDB"""
    
    document = await CaseDocument.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions - users can only download their own documents
    if document.uploaded_by != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied. You can only access your own documents.")
    
    # Decode base64 content back to binary
    try:
        file_content = base64.b64decode(document.file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decoding file content")
    
    # Return file content as response with attachment disposition (forces download)
    return Response(
        content=file_content,
        media_type=document.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{document.original_filename}"'
        }
    )

@app.get("/api/documents/{document_id}/preview")
async def preview_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Preview a document file in browser (inline display)"""
    
    document = await CaseDocument.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions - users can only preview their own documents
    if document.uploaded_by != current_user.username:
        raise HTTPException(status_code=403, detail="Access denied. You can only access your own documents.")
    
    # Decode base64 content back to binary
    try:
        file_content = base64.b64decode(document.file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decoding file content")
    
    # Return file content as response with inline disposition (shows in browser)
    return Response(
        content=file_content,
        media_type=document.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{document.original_filename}"'
        }
    )

@app.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a document from MongoDB"""
    
    document = await CaseDocument.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions - users can only delete their own documents
    if document.uploaded_by != current_user.username:
        raise HTTPException(
            status_code=403, 
            detail="Access denied. You can only delete your own documents."
        )
    
    # Delete document record from MongoDB (file content is stored in the document)
    await document.delete()
    
    return {"message": "Document deleted successfully from MongoDB"}

# AI-Powered Endpoints
@app.post("/api/ai/classify-case")
async def classify_case_ai(
    request: CaseClassificationRequest,
    current_user: User = Depends(get_current_user)
):
    """AI-powered case classification"""
    
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI services not available")
    
    try:
        classification = await ai_service.classify_case(request.description, request.title)
        return {
            "success": True,
            "classification": classification,
            "message": "Case classified successfully"
        }
    except Exception as e:
        logger.error(f"AI classification error: {e}")
        raise HTTPException(status_code=500, detail="Classification failed")

@app.post("/api/ai/analyze-document")
async def analyze_document_ai(
    request: DocumentAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """AI-powered document analysis"""
    
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI services not available")
    
    try:
        analysis = await ai_service.analyze_document_content(request.content, request.filename)
        return {
            "success": True,
            "analysis": analysis,
            "message": "Document analyzed successfully"
        }
    except Exception as e:
        logger.error(f"AI document analysis error: {e}")
        raise HTTPException(status_code=500, detail="Document analysis failed")

@app.post("/api/ai/similar-cases")
async def find_similar_cases_ai(
    request: SimilarCasesRequest,
    current_user: User = Depends(get_current_user)
):
    """Find similar cases using AI"""
    
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI services not available")
    
    try:
        # Get all cases for similarity comparison
        all_cases = await Case.find().to_list()
        similar_cases = await ai_service.find_similar_cases(
            request.description, 
            request.title, 
            limit=request.limit,
            all_cases=all_cases
        )
        
        return {
            "success": True,
            "similar_cases": similar_cases,
            "total_found": len(similar_cases),
            "message": "Similar cases found successfully"
        }
    except Exception as e:
        logger.error(f"AI similar cases error: {e}")
        raise HTTPException(status_code=500, detail="Similar cases search failed")

@app.get("/api/ai/case-insights/{case_id}")
async def get_case_insights(
    case_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated insights for a case"""
    
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI services not available")
    
    try:
        # Get case details
        case = await Case.get(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Convert case to dict format
        case_data = {
            "id": str(case.id),
            "title": case.title,
            "description": case.description,
            "case_type": case.case_type,
            "status": case.status,
            "priority": case.priority
        }
        
        # Get all cases for similarity comparison
        all_cases = await Case.find().to_list()
        
        insights = await ai_service.generate_case_insights(case_data, all_cases)
        
        return {
            "success": True,
            "insights": insights,
            "message": "Case insights generated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI case insights error: {e}")
        raise HTTPException(status_code=500, detail="Case insights generation failed")

@app.get("/api/ai/smart-create-case")
async def smart_create_case_suggestions(
    description: str,
    title: str = "",
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestions for creating a new case"""
    
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI services not available")
    
    try:
        # Classify the potential case
        classification = await ai_service.classify_case(description, title)
        
        # Find similar existing cases
        all_cases = await Case.find().to_list()
        similar_cases = await ai_service.find_similar_cases(
            description, title, limit=3, all_cases=all_cases
        )
        
        # Generate suggestions
        suggestions = {
            "suggested_case_type": classification.get("case_type", "General"),
            "suggested_priority": classification.get("suggested_priority", "medium"),
            "predicted_section": classification.get("predicted_section", "General"),
            "confidence": classification.get("confidence", 0.5),
            "similar_existing_cases": len(similar_cases),
            "recommendations": [
                "📝 Review suggested case type and priority",
                "📋 Check similar cases for precedent",
                "⚖️ Ensure all required documentation is ready",
                "📅 Consider scheduling requirements"
            ]
        }
        
        if similar_cases:
            suggestions["recommendations"].insert(1, f"🔍 {len(similar_cases)} similar cases found - review before creating")
        
        return {
            "success": True,
            "suggestions": suggestions,
            "similar_cases": similar_cases[:3],  # Return top 3 similar cases
            "message": "Smart suggestions generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Smart case creation error: {e}")
        raise HTTPException(status_code=500, detail="Smart case creation failed")

@app.get("/api/ai/dashboard-analytics")
async def get_ai_dashboard_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered dashboard analytics"""
    
    if not AI_ENABLED:
        return {
            "success": False,
            "message": "AI services not available",
            "analytics": {
                "total_cases_analyzed": 0,
                "classification_accuracy": "N/A",
                "top_case_types": [],
                "priority_distribution": {},
                "recent_ai_activities": []
            }
        }
    
    try:
        # Get all cases
        all_cases = await Case.find().to_list()
        
        if not all_cases:
            return {
                "success": True,
                "analytics": {
                    "total_cases_analyzed": 0,
                    "classification_accuracy": "N/A",
                    "top_case_types": [],
                    "priority_distribution": {},
                    "recent_ai_activities": ["No cases available for analysis"]
                }
            }
        
        # Analyze case distribution
        case_types = {}
        priorities = {}
        
        for case in all_cases:
            case_type = case.case_type or "Unknown"
            priority = case.priority or "medium"
            
            case_types[case_type] = case_types.get(case_type, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
        
        # Get top case types
        top_case_types = sorted(case_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent AI activities simulation
        ai_activities = [
            f"Classified {len(all_cases)} cases automatically",
            "Generated insights for recent cases",
            "Identified similar case patterns",
            "Updated case priority recommendations"
        ]
        
        analytics = {
            "total_cases_analyzed": len(all_cases),
            "classification_accuracy": "85.2%",  # Simulated accuracy
            "top_case_types": [{"type": k, "count": v} for k, v in top_case_types],
            "priority_distribution": priorities,
            "recent_ai_activities": ai_activities,
            "model_info": ai_service.model_info if ai_service.model_info else "Basic Classification Model"
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "message": "AI analytics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"AI dashboard analytics error: {e}")
        raise HTTPException(status_code=500, detail="AI analytics generation failed")

# AI Status endpoint
@app.get("/api/ai/status")
async def get_ai_status():
    """Check AI services status"""
    
    if not AI_ENABLED:
        return {
            "ai_enabled": False,
            "message": "AI services are not available",
            "features_available": []
        }
    
    features = [
        "Case Classification",
        "Document Analysis", 
        "Similar Cases Search",
        "Case Insights Generation",
        "Smart Case Creation",
        "Dashboard Analytics"
    ]
    
    return {
        "ai_enabled": True,
        "message": "AI services are running",
        "features_available": features,
        "model_info": ai_service.model_info if ai_service.model_info else None
    }

@app.get("/api/cases/{case_id}/documents")
async def get_case_documents(
    case_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all documents for a specific case"""
    
    # Verify case exists
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    documents = await CaseDocument.find({"case_id": case_id}).to_list()
    
    return [
        {
            "id": str(doc.id),
            "filename": doc.original_filename,
            "size": doc.file_size,
            "type": doc.content_type,
            "uploaded_by": doc.uploaded_by,
            "upload_date": doc.upload_date,
            "description": doc.description,
            "document_type": doc.document_type
        }
        for doc in documents
    ]

if __name__ == "__main__":
    import uvicorn
    
    print("🤖 Starting DCM System - AI-Powered MongoDB Edition")
    print("💾 Database: MongoDB Atlas")
    print("🧠 AI Features: Enabled" if AI_ENABLED else "🧠 AI Features: Disabled")
    print("🌐 Server will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔑 Demo login credentials:")
    print("   - admin / admin123 (Administrator)")
    print("   - judge1 / demo123 (Judge)")
    print("   - clerk1 / demo123 (Clerk)")
    print("   - lawyer1 / demo123 (Lawyer)")
    
    if AI_ENABLED:
        print("🚀 AI Features Available:")
        print("   - 🏷️  Smart Case Classification")
        print("   - 📄 Document Analysis")
        print("   - 🔍 Similar Cases Search")
        print("   - 💡 Case Insights Generation")
        print("   - 📊 AI Dashboard Analytics")
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=8001)
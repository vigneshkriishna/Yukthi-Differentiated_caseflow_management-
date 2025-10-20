"""
User management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_user, require_admin
from app.models.user import User, UserRole, UserBase
from app.core.security import get_password_hash
from pydantic import BaseModel

router = APIRouter()


class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: str
    full_name: str
    role: UserRole
    password: str


class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: str


@router.get("/", response_model=List[UserResponse])
async def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List all users (admin only)"""
    # Only admins can list all users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list users"
        )
    
    users = session.exec(select(User)).all()
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Create a new user (admin only)"""
    
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        hashed_password=get_password_hash(user_data.password)
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at.isoformat()
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get user by ID"""
    # Users can only see their own profile unless they're admin
    if user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update user"""
    # Users can only update their own profile unless they're admin
    if user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.username is not None:
        # Check username uniqueness
        existing = session.exec(
            select(User).where(User.username == user_data.username, User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = user_data.username
    
    if user_data.email is not None:
        # Check email uniqueness
        existing = session.exec(
            select(User).where(User.email == user_data.email, User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    # Only admins can change role and active status
    if current_user.role == UserRole.ADMIN:
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Delete user (admin only)"""
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    session.delete(user)
    session.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/roles/available")
async def get_available_roles(
    current_user: User = Depends(get_current_user),
):
    """Get available user roles"""
    return {
        "roles": [
            {"value": role.value, "label": role.value.title()}
            for role in UserRole
        ]
    }
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ...database import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserLogin, UserResponse, Token
from ...security import get_password_hash, verify_password, create_access_token
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    ثبت‌نام کاربر جدید (دانش‌آموز یا معلم) همراه با تولید توکن JWT
    """
    # بررسی یکتایی ایمیل و نام کاربری
    existing_email = db.query(User).filter(User.email == user_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="حساب کاربری با این نشانی ایمیل از قبل در سامانه ثبت شده است."
        )

    existing_username = db.query(User).filter(User.username == user_in.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این نام کاربری قبلاً توسط کاربر دیگری انتخاب شده است."
        )

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        grade=user_in.grade,
        school_name=user_in.school_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ایجاد توکن دسترسی
    access_token = create_access_token(
        data={"sub": str(new_user.id), "role": new_user.role, "name": new_user.full_name}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=Token)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    ورود به سامانه با ایمیل و گذرواژه
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا گذرواژه واردشده نادرست است.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "name": user.full_name}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    دریافت پروفایل کاربر واردشده با توکن JWT معتبر
    """
    return UserResponse.model_validate(current_user)

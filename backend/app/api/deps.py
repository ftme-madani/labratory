from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Callable, Optional

from ..database import get_db
from ..security import decode_access_token
from ..models.user import User

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    اعتبارسنجی توکن دسترسی Bearer JWT و بازیابی هویت کاربر فعال از دیتابیس
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="احراز هویت انجام نشده است یا توکن معتبر ارسال نشده است.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن دسترسی نامعتبر است یا منقضی شده است.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="شناسه کاربر در توکن وجود ندارد.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="فرمت شناسه کاربر در توکن نامعتبر است.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر متناظر با این توکن در پایگاه داده یافت نشد.",
        )
    return user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    بازیابی اختیاری کاربر (در صورت وجود توکن معتبر) بدون پرتاب خطای 401
    """
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        return None

def require_role(allowed_roles: List[str]) -> Callable:
    """
    کنترل دسترسی نقش‌محور (RBAC) مبتنی بر تزریق وابستگی FastAPI
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            role_persian = {
                "student": "دانش‌آموز",
                "teacher": "معلم",
                "admin": "مدیر سیستم"
            }
            allowed_names = [role_persian.get(r, r) for r in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"دسترسی غیرمجاز. این بخش نیازمند سطح دسترسی {', '.join(allowed_names)} می‌باشد.",
            )
        return current_user
    return role_checker

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserRead
from app.services.users import authenticate_user, create_user

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=201, response_model=UserRead)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = create_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=(str(e)))

    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data)
    if user is None:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

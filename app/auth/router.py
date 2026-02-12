from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.responses import SuccessResponse
from app.auth.security import get_password_hash, verify_password, create_access_token
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=SuccessResponse[UserResponse])
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar novo usuário."""
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=get_password_hash(user_in.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return SuccessResponse(
        data=UserResponse.model_validate(user), message="User created successfully"
    )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Login do usuário (OAuth2 compatible - para Swagger)."""
    # OAuth2 usa 'username', mas passamos o email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    access_token = create_access_token(user.id)

    # Formato OAuth2 padrão
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login/json")
async def login_json(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login do usuário (JSON format - para aplicações client)."""
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    access_token = create_access_token(user.id)

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        },
        "message": "Login successful",
    }


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Retorna informações do usuário logado."""
    return SuccessResponse(
        data=UserResponse.model_validate(current_user),
        message="User retrieved successfully",
    )

# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from sqlalchemy import select
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- OAuth2 Config ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# ============================
# ✅ LOGIN (returns JWT)
# ============================
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticates the user and returns a JWT token.
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = auth_service.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ============================
# ✅ REGISTER USER
# ============================
@router.post("/register")
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a new user.
    """
    auth_service = AuthService(db)

    # ✅ Use ORM-based select query (safe and clean)
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = await auth_service.create_user(user_data)
    return {"message": "User registered successfully", "username": user.username}


# ============================
# ✅ CURRENT USER (token validation)
# ============================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> str:
    """
    Decode the JWT and return the username.
    """
    payload = AuthService.decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    return username

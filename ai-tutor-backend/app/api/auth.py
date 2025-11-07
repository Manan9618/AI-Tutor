# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from datetime import datetime, timedelta, timezone
# from typing import Optional
# from jose import jwt, JWTError, ExpiredSignatureError  # ✅ Correct imports for jose

# # --- Placeholder user DB (replace with real DB in production) ---
# users_db = {
#     "testuser": {"username": "testuser", "password": "testpass", "user_id": "user123"}
# }

# # --- JWT Configuration ---
# SECRET_KEY = "your-secret-key"  # ✅ Should be stored in environment variable in production
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# router = APIRouter()

# # --- Token Response Model ---
# class Token(BaseModel):
#     access_token: str
#     token_type: str

# # --- OAuth2 Setup ---
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# # --- Create JWT Token ---
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# # --- Login Route ---
# @router.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = users_db.get(form_data.username)
#     if not user or user["password"] != form_data.password:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user["user_id"]}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


# # --- Get Current User (Token Validation) ---
# def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
#     """
#     Decode JWT and return user_id (the 'sub' claim).
#     Raises 401 if token is invalid or expired.
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: Optional[str] = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#         return user_id

#     except ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired. Please log in again.",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except JWTError:
#         raise credentials_exception

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

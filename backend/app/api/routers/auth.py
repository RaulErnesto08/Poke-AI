from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.domain.models.auth import UserCreate, UserLogin, UserRead, Token
from app.infra.db import get_db
from app.infra.orm import User

router = APIRouter(tags=["Auth"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with email and password.",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Email already registered"},
    },
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    This endpoint registers a new user using the provided email and password.

    ## Parameters
    - **user_in**: `UserCreate` – Body containing email and password.
    - **db**: Database session dependency.

    ## Returns
    - A `UserRead` object with basic user information.

    ## Possible Errors
    - **400 Bad Request**: The email is already registered.
    """
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticates a user and returns access and refresh tokens.",
    responses={
        200: {"description": "Login successful"},
        400: {"description": "Invalid credentials"},
    },
)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user.

    This endpoint validates the user's credentials and generates access and refresh tokens.

    ## Parameters
    - **user_in**: `UserLogin` – Email and password.
    - **db**: Database session dependency.

    ## Returns
    - A `Token` object containing:
        - **access_token**
        - **refresh_token**

    ## Possible Errors
    - **400 Bad Request**: Invalid email or password.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return Token(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Generates a new access and refresh token for the authenticated user.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Unauthorized"},
    },
)
def refresh(current_user: User = Depends(get_current_user)):
    """
    Refresh authentication tokens.

    This endpoint issues new access and refresh tokens for an authenticated user.

    ## Parameters
    - **current_user**: `User` object from dependency injection.

    ## Returns
    - A new `Token` object with fresh tokens.
    """
    return Token(
        access_token=create_access_token(current_user.email),
        refresh_token=create_refresh_token(current_user.email),
    )


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user",
    description="Returns information about the authenticated user.",
    responses={
        200: {"description": "User information returned successfully"},
        401: {"description": "Unauthorized"},
    },
)
def me(current_user: User = Depends(get_current_user)):
    """
    Get user info.

    Returns the database record for the currently authenticated user.

    ## Parameters
    - **current_user**: Automatically extracted user from the access token.

    ## Returns
    - A `UserRead` representation of the current user.
    """
    return current_user
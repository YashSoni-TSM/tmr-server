from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.connect_db import get_db
from src.schemas.user_schema import UserCreateSchema, UserLoginSchema
from src.controllers.auth_controller import register_user, login_user, logout_user

# ----------------------------------------
# 🔹 Auth Router Setup
# ----------------------------------------

router = APIRouter()

# ----------------------------------------
# 🔹 User Registration
# ----------------------------------------

@router.post("/register", summary="Register a new user")
def register(req: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Handles user registration.

    Parameters:
        - req (UserCreateSchema): User registration data.
        - db (Session): Database session dependency.

    Returns:
        - dict: Success message or error.
    """
    return register_user(req, db)

# ----------------------------------------
# 🔹 User Login
# ----------------------------------------

@router.post("/login", summary="User login and token generation")
def login(req: UserLoginSchema, db: Session = Depends(get_db)):
    """
    Handles user authentication.

    Parameters:
        - req (UserLoginSchema): User login credentials.
        - db (Session): Database session dependency.

    Returns:
        - dict: Access token and success message.
    """
    return login_user(req, db)


# ----------------------------------------
# Logout User
# ----------------------------------------

@router.post("/logout", summary="User logout")
def logout():
    """
    Handles user logout.

    Returns:
        - dict: Success message.
    """
    return logout_user()

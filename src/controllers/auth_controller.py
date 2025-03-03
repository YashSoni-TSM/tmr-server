from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.schemas.user_schema import UserCreateSchema, UserLoginSchema
from src.models.user_model import UserModel
from src.utils.utils import generate_short_uuid, create_access_token

# ----------------------------------------
# 🔹 User Registration
# ----------------------------------------

def register_user(req: UserCreateSchema, db: Session):
    """
    Registers a new user in the system.

    Steps:
    1. Generates a short UUID for the user ID.
    2. Hashes the password for secure storage.
    3. Saves the user record in the database.
    
    Returns:
        Newly created user object.
    """
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = UserModel(
        id=generate_short_uuid(),
        name=req.name,
        email=req.email,
        phone=req.phone,
        password=UserModel.hash_password(req.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "user_name": new_user.name
    }

# ----------------------------------------
# 🔹 User Login
# ----------------------------------------

def login_user(req: UserLoginSchema, db: Session):
    """
    Authenticates a user and issues an access token.

    Steps:
    1. Fetches the user by email.
    2. Verifies the password.
    3. Generates a JWT access token.
    4. Returns the token in a JSON response and sets a secure cookie.

    Returns:
        JSONResponse with user details and access token.
    """
    # Fetch user by email
    user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify password
    if not UserModel.verify_password(req.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Generate access token
    token = create_access_token(data={
        "user_id": user.id,
        "user_name": user.name,
    })

    # Create response with token in JSON and set as an HTTP-only cookie
    response = JSONResponse(
        content={
            "message": "Login successful",
            "user_id": user.id,
            "user_name": user.name,
            "access_token": token
        },
        status_code=200
    )
    response.set_cookie(
        key="access_token", 
        value=token, 
        httponly=True, 
        secure=True, 
        samesite="Lax"
    )

    return response

# ----------------------------------------
# 🔹 User Logout
# ----------------------------------------

def logout_user():
    """
    Logs out the user by clearing the access token cookie.

    Returns:
        JSONResponse with logout message.
    """
    response = JSONResponse(
        content={"message": "Logout successful"},
        status_code=200
    )
    response.delete_cookie(key="access_token")

    return response

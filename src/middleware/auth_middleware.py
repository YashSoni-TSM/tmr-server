from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.utils.utils import decode_access_token, request_cookie
from src.models.user_model import UserModel

# ----------------------------------------
# Auth Middleware
# ----------------------------------------

def get_user_authenticated(req: Request, db: Session = Depends(get_db)):
    """Authenticate user based on the access token from cookies."""
    
    access_token = request_cookie(req)
    if not access_token:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    user_id = decode_access_token(access_token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

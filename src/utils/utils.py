import uuid
import base64
import jwt
from datetime import datetime, timedelta, timezone
from src.config.config import SECRET_KEY,ALGORITHM
from fastapi import HTTPException, Request

# ----------------------------------------
# Utility Functions
# ----------------------------------------

def split_date(date: str) -> int:
    """
    Extracts the year from a column name.

    Example:
        Input: "year_2025"
        Output: 2025
    """
    return int(date.split("_")[1])

# ----------------------------------------
# UUID Generator
# ----------------------------------------

def generate_short_uuid():
    """
    Generates a short UUID-based ID with a specified length.

    - Uses UUID4 for randomness.
    - Encodes in Base64 and removes special characters.
    - Returns only the first `length` characters.

    Example:
        Output: "A1bC2D"
    """
    uid = uuid.uuid4()
    encoded = base64.b64encode(uid.bytes).decode("utf-8")
    
    # Remove special characters to ensure URL-safe ID
    safe_encoded = encoded.replace("/", "").replace("+", "").replace("=", "")
    
    return safe_encoded  # Return the required length


# ----------------------------------------
# Create JWT Access Token
# ----------------------------------------

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ----------------------------------------
# Decode JWT Access Token
# ----------------------------------------

def decode_access_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
# ----------------------------------------
# Request Cookie
# ----------------------------------------

def request_cookie(req:Request):
    token = req.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    return token
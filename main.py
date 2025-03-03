from fastapi import FastAPI, Depends

from src.routes import upload_excel_route, save_metadata_route, auth_route
from src.models import meta_table_model
from src.database.connect_db import engine
from src.middleware.auth_middleware import get_user_authenticated

# ----------------------------------------
# 🔹 FastAPI App Initialization
# ----------------------------------------

app = FastAPI(title="My FastAPI App", version="1.0")

# ----------------------------------------
# 🔹 Database Setup
# ----------------------------------------

meta_table_model.Base.metadata.create_all(bind=engine)

# ----------------------------------------
# 🔹 Route Registration
# ----------------------------------------

app.include_router(
    upload_excel_route.router, 
    prefix="/api/v1", 
    tags=["Upload Excel"], 
    dependencies=[Depends(get_user_authenticated)]
)

app.include_router(
    save_metadata_route.router, 
    prefix="/api/v1", 
    tags=["Save Metadata"]
)

app.include_router(
    auth_route.router, 
    prefix="/api/v1/auth", 
    tags=["Authentication"]
)

# ----------------------------------------
# 🔹 Root Endpoint
# ----------------------------------------

@app.get("/", summary="Root Endpoint")
def read_root():
    """
    Root endpoint for API health check.
    """
    return {"message": "Hello, World!"}

# ----------------------------------------
# 🔹 Application Entry Point
# ----------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)

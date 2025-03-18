from fastapi import FastAPI, Depends
from src.routes import upload_excel_route, auth_route,meta_table_route,extract_graph_data_route
from src.models import meta_table_model
from src.database.connect_db import engine
from src.middleware.auth_middleware import get_user_authenticated
from fastapi.middleware.cors import CORSMiddleware


# ----------------------------------------
# 🔹 FastAPI App Initialization
# ----------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

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
    meta_table_route.router, 
    prefix="/api/v1", 
    tags=["Save Metadata"]
)

app.include_router(
    auth_route.router, 
    prefix="/api/v1/auth", 
    tags=["Authentication"]
)

app.include_router(
    extract_graph_data_route.router,
    prefix="/api/v1",
    tags=["Extract Graph Data"]
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

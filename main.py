from fastapi import FastAPI
from src.routes import upload_excel_route
from src.models import meta_table_model
from src.database.connect_db import engine
app = FastAPI()

meta_table_model.Base.metadata.create_all(bind=engine)

app.include_router(upload_excel_route.router, prefix="/api/v1", tags=["upload_excel"])

@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
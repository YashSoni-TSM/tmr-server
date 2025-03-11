from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.controllers.extract_graph_data_controller import extract_graph_data
from src.schemas.extract_graph_data_schema import ExtractGraphDataSchema


router = APIRouter()

@router.post("/extract-graph-data")
async def extract_graph_data_router(req:ExtractGraphDataSchema, db:Session = Depends(get_db)):
    """
    Extracts data from the database for graph plotting.
    """
    if not req:
        raise HTTPException(status_code=400, detail="Invalid request body.")

    return await extract_graph_data(req,db)